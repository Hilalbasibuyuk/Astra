
from datetime import datetime
from typing import Any
from collections.abc import Sequence

from sqlalchemy.orm import Session

from services.anomaly_detection.service import AnomalyDetectionService
from services.events.models import Event
from services.events.service import EventManagementService


class AnomalyEventCoordinator:
    """Connect anomaly detection with persistent event management."""

    def __init__(
        self,
        db: Session,
        anomaly_service: AnomalyDetectionService | None = None,
    ) -> None:
        self.anomaly_service = (
            anomaly_service or AnomalyDetectionService()
        )
        self.event_service = EventManagementService(db)

    def evaluate_sample(
        self,
        *,
        source_type: str,
        source_id: str,
        event_type: str,
        metric_name: str,
        historical_values: Sequence[float],
        current_value: float,
        severity: str,
        summary: str,
        occurred_at: datetime | None = None,
    ) -> Event | None:
        """Evaluate one new sample and record it if anomalous."""
        values = [*historical_values, current_value]

        predictions = self.anomaly_service.detect_rolling_zscore(
            values
        )

        if not predictions or not predictions[-1]:
            return None

        details: dict[str, Any] = {
            "metric_name": metric_name,
            "current_value": current_value,
            "baseline_sample_count": len(historical_values),
        }

        return self.event_service.record_occurrence(
            source_type=source_type,
            source_id=source_id,
            event_type=event_type,
            severity=severity,
            summary=summary,
            details=details,
            occurred_at=occurred_at,
        )
