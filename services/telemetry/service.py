from questdb.ingress import Sender

from database.questdb.ilp import (
    send_telescope_telemetry,
    send_camera_telemetry,
    send_weather_telemetry,
    send_dome_telemetry,
)
from services.telemetry.models import (
    TelescopeTelemetry,
    CameraTelemetry,
    WeatherTelemetry,
    DomeTelemetry,
)


class TelemetryService:

    def __init__(self, sender: Sender):
        self.sender = sender

    def ingest_telescope(
        self,
        telemetry: TelescopeTelemetry,
    ) -> None:

        send_telescope_telemetry(
            sender=self.sender,
            telescope_id=telemetry.telescope_id,
            azimuth=telemetry.azimuth,
            elevation=telemetry.elevation,
            right_ascension=telemetry.right_ascension,
            declination=telemetry.declination,
            tracking_error=telemetry.tracking_error,
            motor_temperature=telemetry.motor_temperature,
            motor_current=telemetry.motor_current,
            vibration=telemetry.vibration,
            status=telemetry.status,
        )

    def ingest_camera(self, telemetry: CameraTelemetry) -> None:
        send_camera_telemetry(
            sender=self.sender,
            camera_id=telemetry.camera_id,
            sensor_temperature=telemetry.sensor_temperature,
            exposure_time=telemetry.exposure_time,
            gain=telemetry.gain,
            frame_rate=telemetry.frame_rate,
            image_quality=telemetry.image_quality,
            status=telemetry.status,
        )
    def ingest_weather(self, telemetry: WeatherTelemetry) -> None:
        send_weather_telemetry(
            sender=self.sender,
            station_id=telemetry.station_id,
            temperature=telemetry.temperature,
            humidity=telemetry.humidity,
            pressure=telemetry.pressure,
            wind_speed=telemetry.wind_speed,
            seeing=telemetry.seeing,
            cloud_cover=telemetry.cloud_cover,
            status=telemetry.status,
        )

    def ingest_dome(self, telemetry: DomeTelemetry) -> None:
        send_dome_telemetry(
            sender=self.sender,
            dome_id=telemetry.dome_id,
            azimuth=telemetry.azimuth,
            rotation_speed=telemetry.rotation_speed,
            shutter_open=telemetry.shutter_open,
            motor_temperature=telemetry.motor_temperature,
            status=telemetry.status,
        )

    def ingest(self, telemetry) -> None:
        if isinstance(telemetry, TelescopeTelemetry):
            self.ingest_telescope(telemetry)

        elif isinstance(telemetry, CameraTelemetry):
            self.ingest_camera(telemetry)

        elif isinstance(telemetry, WeatherTelemetry):
            self.ingest_weather(telemetry)

        elif isinstance(telemetry, DomeTelemetry):
            self.ingest_dome(telemetry)

        else:
            raise ValueError(
                f"Unsupported telemetry type: {type(telemetry).__name__}"
            )