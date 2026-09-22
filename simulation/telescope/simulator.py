import random
from datetime import datetime, timezone

from services.telemetry.models import TelescopeTelemetry


class TelescopeSimulator:

    def __init__(self, telescope_id: str = "TCS-01"):
        self.telescope_id = telescope_id

        self.azimuth = 120.0
        self.elevation = 45.0

        self.right_ascension = 10.5
        self.declination = 41.2

        self.motor_temperature = 31.0
        self.motor_current = 2.5
        self.vibration = 0.02

        self.status = "NORMAL"

    def step(self) -> TelescopeTelemetry:
        """
        Advance the telescope simulation by one timestep.
        """

        # Small natural movement
        self.azimuth += random.uniform(-0.5, 0.5)
        self.elevation += random.uniform(-0.2, 0.2)

        # Simulated motor load
        self.motor_current += random.uniform(-0.05, 0.05)
        self.motor_current = max(self.motor_current, 0.1)

        # Temperature responds slowly to motor load
        temperature_change = (
            random.uniform(-0.05, 0.05)
            + (self.motor_current - 2.5) * 0.02
        )

        self.motor_temperature += temperature_change

        # Small vibration noise
        self.vibration += random.uniform(-0.002, 0.002)
        self.vibration = max(self.vibration, 0.0)

        # Tracking error
        tracking_error = abs(random.gauss(0.01, 0.003))

        return TelescopeTelemetry(
            timestamp=datetime.now(timezone.utc),
            telescope_id=self.telescope_id,
            azimuth=self.azimuth,
            elevation=self.elevation,
            right_ascension=self.right_ascension,
            declination=self.declination,
            tracking_error=tracking_error,
            motor_temperature=self.motor_temperature,
            motor_current=self.motor_current,
            vibration=self.vibration,
            status=self.status,
        )