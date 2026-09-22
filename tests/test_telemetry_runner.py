import asyncio

from services.telemetry.runner import TelemetryRunner
from simulation.telescope.simulator import TelescopeSimulator


class FakeTelemetryService:

    def __init__(self):
        self.received = []

    def ingest_telescope(self, telemetry):
        self.received.append(telemetry)


def test_telemetry_runner_generates_samples():

    simulator = TelescopeSimulator("RUNNER-TCS-01")

    service = FakeTelemetryService()

    runner = TelemetryRunner(
        simulator=simulator,
        telemetry_service=service,
        interval=0.01,
    )

    async def run_test():

        task = asyncio.create_task(
            runner.run()
        )

        await asyncio.sleep(0.05)

        runner.stop()

        await task

    asyncio.run(run_test())

    assert len(service.received) > 0

    assert all(
        telemetry.telescope_id == "RUNNER-TCS-01"
        for telemetry in service.received
    )