from simulation.dome.simulator import DomeSimulator
from simulation.scenarios.dome import DomeScenarioEngine
from simulation.scenarios.models import ScenarioType


def test_dome_motor_anomaly():
    simulator = DomeSimulator("SCENARIO-DOME-01")
    engine = DomeScenarioEngine()

    engine.start(
        ScenarioType.DOME_MOTOR_ANOMALY
    )

    telemetry = simulator.step()

    result = engine.apply(telemetry)

    assert (
        result.rotation_speed
        > telemetry.rotation_speed
    )

    assert (
        result.motor_temperature
        > telemetry.motor_temperature
    )

    assert result.status == "WARNING"


def test_dome_scenario_stop():
    simulator = DomeSimulator("SCENARIO-DOME-01")
    engine = DomeScenarioEngine()

    engine.start(
        ScenarioType.DOME_MOTOR_ANOMALY
    )

    telemetry = simulator.step()

    engine.apply(telemetry)

    engine.stop()

    result = engine.apply(telemetry)

    assert (
        result.rotation_speed
        == telemetry.rotation_speed
    )

    assert (
        result.motor_temperature
        == telemetry.motor_temperature
    )

    assert result.status == telemetry.status