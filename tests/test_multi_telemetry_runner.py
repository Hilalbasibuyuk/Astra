import asyncio

from services.telemetry.runner import TelemetryRunner
from services.telemetry.multi_runner import MultiTelemetryRunner
from simulation.telescope.simulator import TelescopeSimulator
from simulation.camera.simulator import CameraSimulator
from simulation.weather.simulator import WeatherSimulator
from simulation.dome.simulator import DomeSimulator


class FakeTelemetryService:
    def __init__(self):
        self.received = []

    def ingest(self, telemetry):
        self.received.append(telemetry)


def test_multi_telemetry_runner_runs_all_streams():
    telescope_service = FakeTelemetryService()
    camera_service = FakeTelemetryService()
    weather_service = FakeTelemetryService()
    dome_service = FakeTelemetryService()

    telescope_runner = TelemetryRunner(
        simulator=TelescopeSimulator("MULTI-TCS-01"),
        telemetry_service=telescope_service,
        interval=0.01,
    )

    camera_runner = TelemetryRunner(
        simulator=CameraSimulator("MULTI-CCD-01"),
        telemetry_service=camera_service,
        interval=0.01,
    )

    weather_runner = TelemetryRunner(
        simulator=WeatherSimulator("MULTI-WX-01"),
        telemetry_service=weather_service,
        interval=0.01,
    )

    dome_runner = TelemetryRunner(
        simulator=DomeSimulator("MULTI-DOME-01"),
        telemetry_service=dome_service,
        interval=0.01,
    )

    multi_runner = MultiTelemetryRunner(
        runners=[
            telescope_runner,
            camera_runner,
            weather_runner,
            dome_runner,
        ]
    )

    async def run_test():
        task = asyncio.create_task(multi_runner.run())

        await asyncio.sleep(0.05)

        multi_runner.stop()
        await task

    asyncio.run(run_test())

    assert len(telescope_service.received) > 0
    assert len(camera_service.received) > 0
    assert len(weather_service.received) > 0
    assert len(dome_service.received) > 0

    assert all(
        telemetry.telescope_id == "MULTI-TCS-01"
        for telemetry in telescope_service.received
    )

    assert all(
        telemetry.camera_id == "MULTI-CCD-01"
        for telemetry in camera_service.received
    )

    assert all(
        telemetry.station_id == "MULTI-WX-01"
        for telemetry in weather_service.received
    )

    assert all(
        telemetry.dome_id == "MULTI-DOME-01"
        for telemetry in dome_service.received
    )