from simulation.anomalies.models import (
    AnomalyPattern,
    AnomalyProfile,
)


TELESCOPE_MOTOR_OVERHEATING = AnomalyProfile(
    name="telescope_motor_overheating",
    pattern=AnomalyPattern.GRADUAL_DRIFT,
    magnitude=3.0,
    duration_steps=30,
    severity="high",
    direction=1.0,
)


TELESCOPE_TRACKING_DRIFT = AnomalyProfile(
    name="telescope_tracking_drift",
    pattern=AnomalyPattern.GRADUAL_DRIFT,
    magnitude=0.20,
    duration_steps=40,
    severity="medium",
    direction=1.0,
)


CAMERA_OVERHEATING = AnomalyProfile(
    name="camera_overheating",
    pattern=AnomalyPattern.GRADUAL_DRIFT,
    magnitude=3.0,
    duration_steps=30,
    severity="high",
    direction=1.0,
)


CAMERA_QUALITY_DEGRADATION = AnomalyProfile(
    name="camera_quality_degradation",
    pattern=AnomalyPattern.GRADUAL_DRIFT,
    magnitude=0.30,
    duration_steps=30,
    severity="medium",
    direction=-1.0,
)


WEATHER_DETERIORATION = AnomalyProfile(
    name="weather_deterioration",
    pattern=AnomalyPattern.GRADUAL_DRIFT,
    magnitude=4.0,
    duration_steps=20,
    severity="high",
    direction=1.0,
)


DOME_MOTOR_ANOMALY = AnomalyProfile(
    name="dome_motor_anomaly",
    pattern=AnomalyPattern.OSCILLATION,
    magnitude=0.8,
    duration_steps=20,
    severity="medium",
)