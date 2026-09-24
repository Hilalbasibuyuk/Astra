from enum import Enum


class ScenarioType(str, Enum):
    NORMAL = "normal"

    TELESCOPE_MOTOR_OVERHEATING = (
        "telescope_motor_overheating"
    )

    TELESCOPE_TRACKING_DRIFT = (
        "telescope_tracking_drift"
    )

    CAMERA_OVERHEATING = (
        "camera_overheating"
    )

    CAMERA_QUALITY_DEGRADATION = (
        "camera_quality_degradation"
    )

    WEATHER_DETERIORATION = (
        "weather_deterioration"
    )

    DOME_MOTOR_ANOMALY = (
        "dome_motor_anomaly"
    )