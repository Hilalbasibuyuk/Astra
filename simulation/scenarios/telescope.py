from simulation.anomalies.injector import AnomalyInjector
from simulation.anomalies.profiles import (
    TELESCOPE_MOTOR_OVERHEATING,
    TELESCOPE_TRACKING_DRIFT,
)
from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import TelescopeTelemetry
from simulation.anomalies.models import AnomalyProfile

class TelescopeScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()
        self.injector = AnomalyInjector()

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
            temperature = self.injector.apply(
                telemetry.motor_temperature,
                step,
                TELESCOPE_MOTOR_OVERHEATING,
            )

            current = self.injector.apply(
                telemetry.motor_current,
                step,
                AnomalyProfile(
                    name="motor_current_increase",
                    pattern=TELESCOPE_MOTOR_OVERHEATING.pattern,
                    magnitude=0.15,
                    duration_steps=30,
                ),
            )

            return telemetry.model_copy(
                update={
                    "motor_temperature": temperature,
                    "motor_current": current,
                    "status": "WARNING",
                }
            )

        if self.state.scenario == ScenarioType.TELESCOPE_TRACKING_DRIFT:
            progress = step / TELESCOPE_TRACKING_DRIFT.duration_steps

            tracking_error = (
                telemetry.tracking_error
                + TELESCOPE_TRACKING_DRIFT.direction
                * TELESCOPE_TRACKING_DRIFT.magnitude
                * progress
            )

            return telemetry.model_copy(
                update={
                    "tracking_error": tracking_error,
                    "status": "WARNING",
                }
            )

        return telemetry