from simulation.telescope.simulator import TelescopeSimulator


def test_telescope_simulator_generates_telemetry():

    simulator = TelescopeSimulator("TEST-TCS-01")

    telemetry = simulator.step()

    assert telemetry.telescope_id == "TEST-TCS-01"

    assert telemetry.azimuth is not None
    assert telemetry.elevation is not None

    assert telemetry.motor_temperature > 0
    assert telemetry.motor_current > 0
    assert telemetry.vibration >= 0

    assert telemetry.tracking_error >= 0

    assert telemetry.status == "NORMAL"

def test_telescope_simulator_generates_multiple_samples():

    simulator = TelescopeSimulator("TEST-TCS-01")

    samples = [
        simulator.step()
        for _ in range(100)
    ]

    assert len(samples) == 100

    assert all(
        sample.telescope_id == "TEST-TCS-01"
        for sample in samples
    )

    assert all(
        sample.motor_temperature > 0
        for sample in samples
    )

    assert all(
        sample.motor_current > 0
        for sample in samples
    )