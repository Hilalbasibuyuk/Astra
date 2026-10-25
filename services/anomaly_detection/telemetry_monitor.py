
import logging
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from database.postgres.connection import SessionLocal
from services.anomaly_detection.event_coordinator import (
    AnomalyEventCoordinator,
)
from services.anomaly_detection.service import AnomalyDetectionService
from services.telemetry.models import (
    CameraTelemetry,
    DomeTelemetry,
    TelescopeTelemetry,
    WeatherTelemetry,
)

logger = logging.getLogger(__name__)


class TelemetryAnomalyMonitor:
    """Monitor telemetry samples and persist detected anomalies as events."""

    METRICS: dict[type, tuple[str, str, tuple[str, ...]]] = {
        TelescopeTelemetry: (
            "telescope",
            "telescope_id",
            (
                "tracking_error",
                "motor_temperature",
                "motor_current",
                "vibration",
            ),
        ),
        CameraTelemetry: (
            "camera",
            "camera_id",
            (
                "sensor_temperature",
                "frame_rate",
                "image_quality",
            ),
        ),
        WeatherTelemetry: (
            "weather",
            "station_id",
            (
                "temperature",
                "humidity",
                "pressure",
                "wind_speed",
                "seeing",
                "cloud_cover",
            ),
        ),
        DomeTelemetry: (
            "dome",
            "dome_id",
            (
                "motor_temperature",
                "rotation_speed",
            ),
        ),
    }

    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
        anomaly_service: AnomalyDetectionService | None = None,
        window_size: int = 20,
        min_history: int = 5,
    ) -> None:
        if window_size < 2:
            raise ValueError("window_size must be at least 2.")

        if min_history < 2:
            raise ValueError("min_history must be at least 2.")

        if min_history > window_size:
            raise ValueError(
                "min_history cannot exceed window_size."
            )

        self.session_factory = session_factory
        self.anomaly_service = (
            anomaly_service or AnomalyDetectionService()
        )
        self.window_size = window_size
        self.min_history = min_history

        self._history: dict[
            tuple[str, str, str],
            deque[float],
        ] = defaultdict(
            lambda: deque(maxlen=self.window_size)
        )

    def process(self, telemetry: Any) -> None:
        """Analyze one telemetry sample and record any anomalies."""
        mapping = self.METRICS.get(type(telemetry))

        if mapping is None:
            logger.debug(
                "Skipping unsupported telemetry type: %s",
                type(telemetry).__name__,
            )
            return

        source_type, id_attribute, metric_names = mapping
        source_id = getattr(telemetry, id_attribute)
        occurred_at: datetime = telemetry.timestamp

        detected: list[tuple[str, float, list[float]]] = []

        # Evaluate each metric against its previous samples.
        # The current sample is appended only after evaluation.
        for metric_name in metric_names:
            current_value = float(getattr(telemetry, metric_name))
            key = (source_type, source_id, metric_name)
            historical_values = list(self._history[key])

            if len(historical_values) >= self.min_history:
                values = [*historical_values, current_value]
                predictions = (
                    self.anomaly_service.detect_rolling_zscore(
                        values
                    )
                )

                if predictions and predictions[-1]:
                    detected.append(
                        (
                            metric_name,
                            current_value,
                            historical_values,
                        )
                    )

            self._history[key].append(current_value)

        # Do not open a PostgreSQL session for normal samples.
        if not detected:
            return

        db = self.session_factory()

        try:
            coordinator = AnomalyEventCoordinator(
                db=db,
                anomaly_service=self.anomaly_service,
            )

            for metric_name, current_value, historical_values in detected:
                coordinator.evaluate_sample(
                    source_type=source_type,
                    source_id=source_id,
                    event_type=f"{metric_name}_anomaly",
                    metric_name=metric_name,
                    historical_values=historical_values,
                    current_value=current_value,
                    severity="medium",
                    summary=(
                        f"Anomalous {metric_name} detected "
                        f"for {source_type} {source_id}."
                    ),
                    occurred_at=occurred_at,
                )

            db.commit()

            logger.warning(
                "Telemetry anomalies recorded: source_type=%s "
                "source_id=%s metrics=%s",
                source_type,
                source_id,
                [item[0] for item in detected],
            )

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to persist telemetry anomalies: "
                "source_type=%s source_id=%s",
                source_type,
                source_id,
            )

        finally:
            db.close()
