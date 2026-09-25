from simulation.scenarios.models import ScenarioType
from simulation.scenarios.weather import WeatherScenarioEngine
from simulation.weather.simulator import WeatherSimulator


def test_weather_deterioration():
    simulator = WeatherSimulator("SCENARIO-WX-01")
    engine = WeatherScenarioEngine()

    engine.start(
        ScenarioType.WEATHER_DETERIORATION
    )

    telemetry = simulator.step()

    result = engine.apply(telemetry)

    assert result.wind_speed > telemetry.wind_speed
    assert result.cloud_cover > telemetry.cloud_cover
    assert result.seeing > telemetry.seeing
    assert result.status == "WARNING"


def test_weather_scenario_stop():
    simulator = WeatherSimulator("SCENARIO-WX-01")
    engine = WeatherScenarioEngine()

    engine.start(
        ScenarioType.WEATHER_DETERIORATION
    )

    telemetry = simulator.step()

    engine.apply(telemetry)

    engine.stop()

    result = engine.apply(telemetry)

    assert result.wind_speed == telemetry.wind_speed
    assert result.cloud_cover == telemetry.cloud_cover
    assert result.status == telemetry.status

def test_weather_deterioration_is_gradual():
    engine = WeatherScenarioEngine()

    engine.start(
        ScenarioType.WEATHER_DETERIORATION
    )

    simulator = WeatherSimulator()

    first = engine.apply(simulator.step())
    second = engine.apply(simulator.step())

    assert second.wind_speed > first.wind_speed
    assert second.cloud_cover > first.cloud_cover
    assert second.seeing > first.seeing