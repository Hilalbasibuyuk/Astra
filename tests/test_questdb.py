from database.questdb.connection import create_ilp_sender
from database.questdb.ilp import send_telescope_telemetry


def test_questdb_ilp_connection():

    with create_ilp_sender() as sender:

        send_telescope_telemetry(
            sender=sender,
            telescope_id="TEST-TCS-01",
            azimuth=120.0,
            elevation=45.0,
            right_ascension=10.5,
            declination=41.2,
            tracking_error=0.01,
            motor_temperature=31.5,
            motor_current=2.4,
            vibration=0.02,
            status="TEST",
        )

        sender.flush()