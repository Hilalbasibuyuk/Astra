from simulation.scenarios.models import ScenarioType
from simulation.scenarios.telescope import TelescopeScenarioEngine
from simulation.telescope.simulator import TelescopeSimulator


def test_telescope_normal_scenario():
    simulator = TelescopeSimulator("SCENARIO-TCS-01")
    engine = TelescopeScenarioEngine()

    telemetry = simulator.step()
    result = engine.apply(telemetry)

    assert result.motor_temperature == telemetry.motor_temperature
    assert result.motor_current == telemetry.motor_current
    assert result.status == "NORMAL"


def test_motor_overheating_is_gradual():
    engine = TelescopeScenarioEngine()

    engine.start(
        ScenarioType.TELESCOPE_MOTOR_OVERHEATING
    )

    first = engine.apply(
        TelescopeSimulator().step()
    )

    second = engine.apply(
        TelescopeSimulator().step()
    )

    assert first.status == "WARNING"
    assert second.status == "WARNING"

    assert second.motor_temperature > first.motor_temperature


def test_tracking_drift_is_gradual():
    engine = TelescopeScenarioEngine()

    engine.start(
        ScenarioType.TELESCOPE_TRACKING_DRIFT
    )

    simulator = TelescopeSimulator()

    first = engine.apply(simulator.step())
    second = engine.apply(simulator.step())

    assert first.status == "WARNING"
    assert second.status == "WARNING"

    assert second.tracking_error > first.tracking_error


def test_telescope_scenario_stop():
    simulator = TelescopeSimulator("SCENARIO-TCS-01")
    engine = TelescopeScenarioEngine()

    engine.start(
        ScenarioType.TELESCOPE_MOTOR_OVERHEATING
    )

    telemetry = simulator.step()

    anomalous = engine.apply(telemetry)

    engine.stop()

    normal = engine.apply(telemetry)

    assert anomalous.motor_temperature > telemetry.motor_temperature
    assert normal.motor_temperature == telemetry.motor_temperature
    assert normal.status == telemetry.status