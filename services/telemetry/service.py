from questdb.ingress import Sender

from database.questdb.ilp import send_telescope_telemetry
from services.telemetry.models import TelescopeTelemetry


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