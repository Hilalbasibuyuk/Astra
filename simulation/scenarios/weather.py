from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import WeatherTelemetry


class WeatherScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()

    def start(self, scenario: ScenarioType) -> None:
        if scenario != ScenarioType.WEATHER_DETERIORATION:
            raise ValueError(
                f"Unsupported weather scenario: {scenario}"
            )

        self.state.start(scenario)

    def stop(self) -> None:
        self.state.stop()

    def apply(
        self,
        telemetry: WeatherTelemetry,
    ) -> WeatherTelemetry:

        if not self.state.active:
            return telemetry

        step = self.state.next_step()

        return telemetry.model_copy(
            update={
                "wind_speed": (
                    telemetry.wind_speed
                    + 2.0 * step
                ),
                "cloud_cover": min(
                    1.0,
                    telemetry.cloud_cover
                    + 0.08 * step,
                ),
                "seeing": (
                    telemetry.seeing
                    + 0.2 * step
                ),
                "status": "WARNING",
            }
        )