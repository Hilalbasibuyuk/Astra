import random
from datetime import datetime, timezone

from services.telemetry.models import WeatherTelemetry


class WeatherSimulator:
    def __init__(self, station_id: str = "WX-01"):
        self.station_id = station_id
        self.temperature = 12.0
        self.humidity = 55.0
        self.pressure = 1013.0
        self.wind_speed = 3.0
        self.seeing = 1.2
        self.cloud_cover = 0.1
        self.status = "NORMAL"

    def step(self) -> WeatherTelemetry:
        self.temperature += random.uniform(-0.1, 0.1)
        self.humidity += random.uniform(-0.5, 0.5)
        self.pressure += random.uniform(-0.3, 0.3)
        self.wind_speed += random.uniform(-0.2, 0.2)
        self.seeing += random.uniform(-0.05, 0.05)
        self.cloud_cover += random.uniform(-0.02, 0.02)

        self.humidity = min(max(self.humidity, 0.0), 100.0)
        self.wind_speed = max(self.wind_speed, 0.0)
        self.seeing = max(self.seeing, 0.0)
        self.cloud_cover = min(max(self.cloud_cover, 0.0), 1.0)

        return WeatherTelemetry(
            timestamp=datetime.now(timezone.utc),
            station_id=self.station_id,
            temperature=self.temperature,
            humidity=self.humidity,
            pressure=self.pressure,
            wind_speed=self.wind_speed,
            seeing=self.seeing,
            cloud_cover=self.cloud_cover,
            status=self.status,
        )