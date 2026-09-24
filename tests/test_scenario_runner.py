import asyncio

from services.telemetry.runner import TelemetryRunner
from simulation.scenarios.models import ScenarioType
from simulation.scenarios.telescope import TelescopeScenarioEngine
from simulation.telescope.simulator import TelescopeSimulator


class FakeTelemetryService:
    def __init__(self):
        self.received = []

    def ingest(self, telemetry):
        self.received.append(telemetry)


def test_runner_applies_scenario():
    simulator = TelescopeSimulator(
        "SCENARIO-RUNNER-TCS"
    )

    service = FakeTelemetryService()

    scenario_engine = TelescopeScenarioEngine()

    scenario_engine.start(
        ScenarioType.TELESCOPE_MOTOR_OVERHEATING
    )

    runner = TelemetryRunner(
        simulator=simulator,
        telemetry_service=service,
        interval=0.01,
        scenario_engine=scenario_engine,
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
        telemetry.status == "WARNING"
        for telemetry in service.received
    )

    assert all(
        telemetry.motor_temperature > 31.0
        for telemetry in service.received
    )