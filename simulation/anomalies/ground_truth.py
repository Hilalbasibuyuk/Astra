from datetime import datetime, timedelta
from uuid import uuid4

from services.anomaly_detection.models import AnomalyEvent
from simulation.anomalies.models import AnomalyProfile


class GroundTruthGenerator:
    """Generates ground-truth anomaly events for simulated telemetry."""

    def create_event(
        self,
        profile: AnomalyProfile,
        source_type: str,
        source_id: str,
        metric: str,
        start_time: datetime,
        step_seconds: int = 1,
        description: str = "",
    ) -> AnomalyEvent:
        end_time = start_time + timedelta(
            seconds=profile.duration_steps * step_seconds
        )

        return AnomalyEvent(
            event_id=str(uuid4()),
            source_type=source_type,
            source_id=source_id,
            metric=metric,
            anomaly_type=self._resolve_anomaly_type(profile.name),
            start_time=start_time,
            end_time=end_time,
            severity=profile.severity,
            description=description or profile.name,
        )

    @staticmethod
    def _resolve_anomaly_type(name: str):
        from services.anomaly_detection.models import AnomalyType

        mapping = {
            "telescope_motor_overheating": AnomalyType.MOTOR_OVERHEATING,
            "telescope_tracking_drift": AnomalyType.TRACKING_DRIFT,
            "camera_overheating": AnomalyType.CAMERA_OVERHEATING,
            "camera_quality_degradation": AnomalyType.IMAGE_QUALITY_DEGRADATION,
            "weather_deterioration": AnomalyType.WEATHER_DETERIORATION,
            "dome_motor_anomaly": AnomalyType.DOME_MOTOR_ANOMALY,
        }

        if name not in mapping:
            raise ValueError(f"Unknown anomaly profile: {name}")

        return mapping[name]