from dataclasses import dataclass
from enum import Enum


class AnomalyPattern(str, Enum):
    SUDDEN_SPIKE = "sudden_spike"
    GRADUAL_DRIFT = "gradual_drift"
    STUCK_SENSOR = "stuck_sensor"
    OSCILLATION = "oscillation"
    MISSING_DATA = "missing_data"
    COMMUNICATION_LOSS = "communication_loss"


@dataclass
class AnomalyProfile:
    name: str
    pattern: AnomalyPattern

    magnitude: float = 1.0
    duration_steps: int = 20
    

    severity: str = "medium"

    direction: float = 1.0

    warmup_steps: int = 0

    