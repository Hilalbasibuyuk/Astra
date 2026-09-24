from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import DomeTelemetry


class DomeScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()

    def start(self, scenario: ScenarioType) -> None:
        if scenario != ScenarioType.DOME_MOTOR_ANOMALY:
            raise ValueError(
                f"Unsupported dome scenario: {scenario}"
            )

        self.state.start(scenario)

    def stop(self) -> None:
        self.state.stop()

    def apply(
        self,
        telemetry: DomeTelemetry,
    ) -> DomeTelemetry:

        if not self.state.active:
            return telemetry

        step = self.state.next_step()

        return telemetry.model_copy(
            update={
                "rotation_speed": (
                    telemetry.rotation_speed
                    + 0.5 * step
                ),
                "motor_temperature": (
                    telemetry.motor_temperature
                    + 1.5 * step
                ),
                "status": "WARNING",
            }
        )