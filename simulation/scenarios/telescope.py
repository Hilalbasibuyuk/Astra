from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import TelescopeTelemetry


class TelescopeScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()

    def start(self, scenario: ScenarioType) -> None:
        if scenario not in {
            ScenarioType.TELESCOPE_MOTOR_OVERHEATING,
            ScenarioType.TELESCOPE_TRACKING_DRIFT,
        }:
            raise ValueError(
                f"Unsupported telescope scenario: {scenario}"
            )

        self.state.start(scenario)

    def stop(self) -> None:
        self.state.stop()

    def apply(
        self,
        telemetry: TelescopeTelemetry,
    ) -> TelescopeTelemetry:

        if not self.state.active:
            return telemetry

        step = self.state.next_step()

        if (
            self.state.scenario
            == ScenarioType.TELESCOPE_MOTOR_OVERHEATING
        ):
            return telemetry.model_copy(
                update={
                    "motor_temperature": (
                        telemetry.motor_temperature
                        + 2.0 * step
                    ),
                    "motor_current": (
                        telemetry.motor_current
                        + 0.15 * step
                    ),
                    "status": "WARNING",
                }
            )

        if (
            self.state.scenario
            == ScenarioType.TELESCOPE_TRACKING_DRIFT
        ):
            return telemetry.model_copy(
                update={
                    "tracking_error": (
                        telemetry.tracking_error
                        + 0.01 * step
                    ),
                    "status": "WARNING",
                }
            )

        return telemetry