from simulation.dome.simulator import DomeSimulator


def test_dome_simulator_generates_valid_telemetry():
    simulator = DomeSimulator("TEST-DOME-01")

    telemetry = simulator.step()

    assert telemetry.dome_id == "TEST-DOME-01"
    assert 0 <= telemetry.azimuth < 360
    assert telemetry.rotation_speed >= 0
    assert telemetry.motor_temperature > 0
    assert isinstance(telemetry.shutter_open, bool)


def test_dome_simulator_generates_multiple_samples():
    simulator = DomeSimulator("TEST-DOME-02")

    samples = [simulator.step() for _ in range(100)]

    assert len(samples) == 100

    assert all(
        sample.dome_id == "TEST-DOME-02"
        for sample in samples
    )

    assert all(
        0 <= sample.azimuth < 360
        for sample in samples
    )

    assert all(
        sample.rotation_speed >= 0
        for sample in samples
    )


def test_dome_simulator_preserves_state():
    simulator = DomeSimulator("TEST-DOME-03")

    first = simulator.step()
    second = simulator.step()

    assert first.timestamp <= second.timestamp
    assert first.dome_id == second.dome_id