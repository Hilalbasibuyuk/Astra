from simulation.anomalies.injector import AnomalyInjector
from simulation.anomalies.profiles import (
    DOME_MOTOR_ANOMALY,
)
from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import DomeTelemetry
from simulation.anomalies.models import AnomalyProfile

class DomeScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()
        self.injector = AnomalyInjector()

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

        rotation_speed = self.injector.apply(
            telemetry.rotation_speed,
            step,
            DOME_MOTOR_ANOMALY,
        )

        motor_temperature = self.injector.apply(
            telemetry.motor_temperature,
            step,
            DOME_MOTOR_ANOMALY,
        )

        return telemetry.model_copy(
            update={
                "rotation_speed": max(rotation_speed, 0.0),
                "motor_temperature": motor_temperature,
                "status": "WARNING",
            }
        )