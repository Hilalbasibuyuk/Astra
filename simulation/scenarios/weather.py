from simulation.anomalies.injector import AnomalyInjector
from simulation.anomalies.profiles import (
    WEATHER_DETERIORATION,
)
from simulation.scenarios.models import ScenarioType
from simulation.scenarios.state import ScenarioState
from services.telemetry.models import WeatherTelemetry


class WeatherScenarioEngine:
    def __init__(self):
        self.state = ScenarioState()
        self.injector = AnomalyInjector()

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

        wind_speed = self.injector.apply(
            telemetry.wind_speed,
            step,
            WEATHER_DETERIORATION,
        )

        cloud_cover = self.injector.apply(
            telemetry.cloud_cover,
            step,
            WEATHER_DETERIORATION,
        )

        seeing = self.injector.apply(
            telemetry.seeing,
            step,
            WEATHER_DETERIORATION,
        )

        return telemetry.model_copy(
            update={
                "wind_speed": max(wind_speed, 0.0),
                "cloud_cover": min(cloud_cover, 1.0),
                "seeing": max(seeing, 0.0),
                "status": "WARNING",
            }
        )