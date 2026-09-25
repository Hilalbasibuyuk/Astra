from datetime import datetime

from simulation.dataset import DatasetGenerator
from services.telemetry.models import TelescopeTelemetry


def test_telescope_dataset_export(tmp_path):
    generator = DatasetGenerator(output_dir=str(tmp_path))

    records = [
        TelescopeTelemetry(
            timestamp=datetime(2026, 1, 1, 0, 0, 0),
            telescope_id="telescope-01",
            azimuth=120.0,
            elevation=45.0,
            right_ascension=10.0,
            declination=20.0,
            tracking_error=0.01,
            motor_temperature=35.0,
            motor_current=2.0,
            vibration=0.1,
            status="OK",
        ),
        TelescopeTelemetry(
            timestamp=datetime(2026, 1, 1, 0, 0, 1),
            telescope_id="telescope-01",
            azimuth=120.1,
            elevation=45.1,
            right_ascension=10.1,
            declination=20.1,
            tracking_error=0.02,
            motor_temperature=35.1,
            motor_current=2.1,
            vibration=0.1,
            status="OK",
        ),
    ]

    output = generator.export_telescope(records)

    assert output.exists()

    content = output.read_text(encoding="utf-8")

    assert "timestamp" in content
    assert "tracking_error" in content
    assert "telescope-01" in content