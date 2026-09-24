from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import CameraTelemetry


class CameraScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()

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
            return telemetry.model_copy(
                update={
                    "sensor_temperature": (
                        telemetry.sensor_temperature
                        + 1.5 * step
                    ),
                    "status": "WARNING",
                }
            )

        if (
            self.state.scenario
            == ScenarioType.CAMERA_QUALITY_DEGRADATION
        ):
            quality = max(
                0.0,
                telemetry.image_quality
                - 0.05 * step,
            )

            return telemetry.model_copy(
                update={
                    "image_quality": quality,
                    "status": "WARNING",
                }
            )

        return telemetry