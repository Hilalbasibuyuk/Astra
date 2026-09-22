from datetime import datetime, timezone

from questdb.ingress import Sender

from database.questdb.connection import create_ilp_sender


def send_telescope_telemetry(
    sender: Sender,
    telescope_id: str,
    azimuth: float,
    elevation: float,
    right_ascension: float,
    declination: float,
    tracking_error: float,
    motor_temperature: float,
    motor_current: float,
    vibration: float,
    status: str,
) -> None:

    timestamp = datetime.now(timezone.utc)

    sender.row(
        "telescope_telemetry",
        symbols={
            "telescope_id": telescope_id,
            "status": status,
        },
        columns={
            "azimuth": azimuth,
            "elevation": elevation,
            "right_ascension": right_ascension,
            "declination": declination,
            "tracking_error": tracking_error,
            "motor_temperature": motor_temperature,
            "motor_current": motor_current,
            "vibration": vibration,
        },
        at=timestamp,
    )