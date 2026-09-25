from datetime import datetime

from simulation.anomalies.ground_truth import GroundTruthGenerator
from simulation.anomalies.profiles import TELESCOPE_TRACKING_DRIFT


def test_ground_truth_event_generation():
    generator = GroundTruthGenerator()

    start_time = datetime(2026, 1, 1, 0, 0, 0)

    event = generator.create_event(
        profile=TELESCOPE_TRACKING_DRIFT,
        source_type="telescope",
        source_id="telescope-01",
        metric="tracking_error",
        start_time=start_time,
        step_seconds=1,
        description="Tracking error is gradually increasing.",
    )

    assert event.source_type == "telescope"
    assert event.source_id == "telescope-01"
    assert event.metric == "tracking_error"
    assert event.anomaly_type.value == "tracking_drift"
    assert event.start_time == start_time
    assert event.end_time is not None
    assert event.severity == "medium"