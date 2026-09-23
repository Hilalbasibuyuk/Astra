import random
from datetime import datetime, timezone

from services.telemetry.models import DomeTelemetry


class DomeSimulator:
    def __init__(self, dome_id: str = "DOME-01"):
        self.dome_id = dome_id
        self.azimuth = 120.0
        self.rotation_speed = 0.0
        self.shutter_open = True
        self.motor_temperature = 28.0
        self.status = "NORMAL"

    def step(self) -> DomeTelemetry:
        self.azimuth += random.uniform(-0.5, 0.5)
        self.azimuth %= 360.0

        self.rotation_speed = abs(random.uniform(-0.2, 0.2))

        self.motor_temperature += random.uniform(-0.05, 0.05)

        return DomeTelemetry(
            timestamp=datetime.now(timezone.utc),
            dome_id=self.dome_id,
            azimuth=self.azimuth,
            rotation_speed=self.rotation_speed,
            shutter_open=self.shutter_open,
            motor_temperature=self.motor_temperature,
            status=self.status,
        )