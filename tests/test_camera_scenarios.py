from simulation.scenarios.camera import CameraScenarioEngine
from simulation.scenarios.models import ScenarioType
from simulation.camera.simulator import CameraSimulator


def test_camera_overheating():
    simulator = CameraSimulator("SCENARIO-CCD-01")
    engine = CameraScenarioEngine()

    engine.start(
        ScenarioType.CAMERA_OVERHEATING
    )

    telemetry = simulator.step()

    result = engine.apply(telemetry)

    assert (
        result.sensor_temperature
        > telemetry.sensor_temperature
    )

    assert result.status == "WARNING"


def test_camera_quality_degradation():
    simulator = CameraSimulator("SCENARIO-CCD-01")
    engine = CameraScenarioEngine()

    engine.start(
        ScenarioType.CAMERA_QUALITY_DEGRADATION
    )

    telemetry = simulator.step()

    result = engine.apply(telemetry)

    assert (
        result.image_quality
        < telemetry.image_quality
    )

    assert result.status == "WARNING"


def test_camera_scenario_stop():
    simulator = CameraSimulator("SCENARIO-CCD-01")
    engine = CameraScenarioEngine()

    engine.start(
        ScenarioType.CAMERA_OVERHEATING
    )

    telemetry = simulator.step()

    engine.apply(telemetry)

    engine.stop()

    result = engine.apply(telemetry)

    assert (
        result.sensor_temperature
        == telemetry.sensor_temperature
    )

    assert result.status == telemetry.status