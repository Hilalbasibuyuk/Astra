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


def test_telescope_motor_overheating():
    simulator = TelescopeSimulator("SCENARIO-TCS-01")
    engine = TelescopeScenarioEngine()

    engine.start(
        ScenarioType.TELESCOPE_MOTOR_OVERHEATING
    )

    telemetry = simulator.step()

    result_1 = engine.apply(telemetry)
    result_2 = engine.apply(telemetry)

    assert result_1.motor_temperature > telemetry.motor_temperature
    assert result_2.motor_temperature > result_1.motor_temperature

    assert result_1.motor_current > telemetry.motor_current
    assert result_2.motor_current > result_1.motor_current

    assert result_1.status == "WARNING"
    assert result_2.status == "WARNING"


def test_telescope_tracking_drift():
    simulator = TelescopeSimulator("SCENARIO-TCS-01")
    engine = TelescopeScenarioEngine()

    engine.start(
        ScenarioType.TELESCOPE_TRACKING_DRIFT
    )

    telemetry = simulator.step()

    result = engine.apply(telemetry)

    assert result.tracking_error > telemetry.tracking_error
    assert result.status == "WARNING"


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