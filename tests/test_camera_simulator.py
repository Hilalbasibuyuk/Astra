from simulation.camera.simulator import CameraSimulator


def test_camera_simulator_generates_valid_telemetry():
    simulator = CameraSimulator("TEST-CCD-01")

    telemetry = simulator.step()

    assert telemetry.camera_id == "TEST-CCD-01"
    assert telemetry.exposure_time > 0
    assert telemetry.gain >= 0
    assert telemetry.frame_rate >= 0
    assert 0 <= telemetry.image_quality <= 1


def test_camera_simulator_generates_multiple_samples():
    simulator = CameraSimulator("TEST-CCD-02")

    samples = [simulator.step() for _ in range(100)]

    assert len(samples) == 100

    assert all(
        sample.camera_id == "TEST-CCD-02"
        for sample in samples
    )

    assert all(
        sample.exposure_time > 0
        for sample in samples
    )

    assert all(
        0 <= sample.image_quality <= 1
        for sample in samples
    )


def test_camera_simulator_preserves_state():
    simulator = CameraSimulator("TEST-CCD-03")

    first = simulator.step()
    second = simulator.step()

    assert first.timestamp <= second.timestamp

    assert first.camera_id == second.camera_id