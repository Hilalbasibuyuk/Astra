from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AnomalyType(str, Enum):
    MOTOR_OVERHEATING = "motor_overheating"
    TRACKING_DRIFT = "tracking_drift"
    CAMERA_OVERHEATING = "camera_overheating"
    IMAGE_QUALITY_DEGRADATION = "image_quality_degradation"
    WEATHER_DETERIORATION = "weather_deterioration"
    DOME_MOTOR_ANOMALY = "dome_motor_anomaly"
    SENSOR_SPIKE = "sensor_spike"
    SENSOR_DRIFT = "sensor_drift"
    STUCK_SENSOR = "stuck_sensor"
    OSCILLATION = "oscillation"
    MISSING_DATA = "missing_data"
    COMMUNICATION_LOSS = "communication_loss"


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyLabel(BaseModel):
    timestamp: datetime
    source_type: str
    source_id: str
    metric: str

    is_anomaly: bool = False

    anomaly_type: AnomalyType | None = None
    severity: AnomalySeverity | None = None

    scenario_step: int | None = Field(default=None, ge=0)


class AnomalyResult(BaseModel):
    timestamp: datetime
    source_type: str
    source_id: str
    metric: str

    is_anomaly: bool
    score: float

    detector: str

    anomaly_type: AnomalyType | None = None

class AnomalyEvent(BaseModel):
    event_id: str

    source_type: str
    source_id: str

    metric: str
    anomaly_type: AnomalyType

    start_time: datetime
    end_time: datetime | None = None

    severity: AnomalySeverity

    description: str = ""