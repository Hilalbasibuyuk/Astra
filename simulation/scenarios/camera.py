from simulation.anomalies.injector import AnomalyInjector
from simulation.anomalies.profiles import (
    CAMERA_OVERHEATING,
    CAMERA_QUALITY_DEGRADATION,
)
from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import CameraTelemetry
from simulation.anomalies.models import AnomalyProfile

class CameraScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()
        self.injector = AnomalyInjector()

    def start(self, scenario: ScenarioType) -> None:
        if scenario not in {
            ScenarioType.CAMERA_OVERHEATING,
            ScenarioType.CAMERA_QUALITY_DEGRADATION,
        }:
            raise ValueError(
                f"Unsupported camera scenario: {scenario}"
            )

        self.state.start(scenario)

    def stop(self) -> None:
        self.state.stop()

    def apply(
        self,
        telemetry: CameraTelemetry,
    ) -> CameraTelemetry:

        if not self.state.active:
            return telemetry

        step = self.state.next_step()

        if (
            self.state.scenario
            == ScenarioType.CAMERA_OVERHEATING
        ):
            temperature = self.injector.apply(
                telemetry.sensor_temperature,
                step,
                CAMERA_OVERHEATING,
            )

            return telemetry.model_copy(
                update={
                    "sensor_temperature": temperature,
                    "status": "WARNING",
                }
            )

        if (
            self.state.scenario
            == ScenarioType.CAMERA_QUALITY_DEGRADATION
        ):
            quality = self.injector.apply(
                telemetry.image_quality,
                step,
                CAMERA_QUALITY_DEGRADATION,
            )

            quality = max(0.0, quality)

            return telemetry.model_copy(
                update={
                    "image_quality": quality,
                    "status": "WARNING",
                }
            )

        return telemetry