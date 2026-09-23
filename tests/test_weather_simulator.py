from simulation.weather.simulator import WeatherSimulator


def test_weather_simulator_generates_valid_telemetry():
    simulator = WeatherSimulator("TEST-WX-01")

    telemetry = simulator.step()

    assert telemetry.station_id == "TEST-WX-01"
    assert 0 <= telemetry.humidity <= 100
    assert telemetry.pressure > 0
    assert telemetry.wind_speed >= 0
    assert telemetry.seeing >= 0
    assert 0 <= telemetry.cloud_cover <= 1


def test_weather_simulator_generates_multiple_samples():
    simulator = WeatherSimulator("TEST-WX-02")

    samples = [simulator.step() for _ in range(100)]

    assert len(samples) == 100

    assert all(
        sample.station_id == "TEST-WX-02"
        for sample in samples
    )

    assert all(
        0 <= sample.humidity <= 100
        for sample in samples
    )

    assert all(
        0 <= sample.cloud_cover <= 1
        for sample in samples
    )


def test_weather_simulator_preserves_state():
    simulator = WeatherSimulator("TEST-WX-03")

    first = simulator.step()
    second = simulator.step()

    assert first.timestamp <= second.timestamp
    assert first.station_id == second.station_id