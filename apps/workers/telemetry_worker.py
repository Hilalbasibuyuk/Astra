import asyncio
import logging

from database.questdb.connection import create_ilp_sender
from services.telemetry.runner import TelemetryRunner
from services.telemetry.service import TelemetryService
from simulation.telescope.simulator import TelescopeSimulator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def main():

    simulator = TelescopeSimulator("TCS-01")

    with create_ilp_sender() as sender:

        telemetry_service = TelemetryService(sender)

        runner = TelemetryRunner(
            simulator=simulator,
            telemetry_service=telemetry_service,
            interval=1.0,
        )

        try:
            await runner.run()

        except KeyboardInterrupt:
            runner.stop()


if __name__ == "__main__":
    asyncio.run(main())