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

def test_dome_motor_anomaly_is_oscillatory():
    engine = DomeScenarioEngine()

    engine.start(
        ScenarioType.DOME_MOTOR_ANOMALY
    )

    simulator = DomeSimulator()

    first = engine.apply(simulator.step())
    second = engine.apply(simulator.step())

    assert first.status == "WARNING"
    assert second.status == "WARNING"

    assert first.motor_temperature != second.motor_temperature