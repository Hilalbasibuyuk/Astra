import random
from datetime import datetime, timezone

from services.telemetry.models import CameraTelemetry


class CameraSimulator:
    def __init__(self, camera_id: str = "CCD-01"):
        self.camera_id = camera_id
        self.sensor_temperature = -20.0
        self.exposure_time = 10.0
        self.gain = 1.0
        self.frame_rate = 2.0
        self.status = "NORMAL"

    def step(self) -> CameraTelemetry:
        self.sensor_temperature += random.uniform(-0.05, 0.05)

        self.exposure_time += random.uniform(-0.1, 0.1)
        self.exposure_time = max(self.exposure_time, 0.1)

        self.gain += random.uniform(-0.02, 0.02)
        self.gain = max(self.gain, 0.0)

        self.frame_rate += random.uniform(-0.05, 0.05)
        self.frame_rate = max(self.frame_rate, 0.0)

        temperature_penalty = max(
            0.0,
            (self.sensor_temperature + 15.0) / 20.0,
        )

        image_quality = 1.0 - temperature_penalty * 0.2
        image_quality += random.uniform(-0.02, 0.02)
        image_quality = min(max(image_quality, 0.0), 1.0)

        return CameraTelemetry(
            timestamp=datetime.now(timezone.utc),
            camera_id=self.camera_id,
            sensor_temperature=self.sensor_temperature,
            exposure_time=self.exposure_time,
            gain=self.gain,
            frame_rate=self.frame_rate,
            image_quality=image_quality,
            status=self.status,
        )