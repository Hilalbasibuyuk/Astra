import asyncio
import logging

from services.telemetry.runner import TelemetryRunner

logger = logging.getLogger(__name__)


class MultiTelemetryRunner:
    def __init__(
        self,
        runners: list[TelemetryRunner],
    ):
        self.runners = runners
        self._tasks: list[asyncio.Task] = []

    async def run(self) -> None:
        if not self.runners:
            logger.warning("No telemetry runners configured.")
            return

        logger.info(
            "Starting %d telemetry runners",
            len(self.runners),
        )

        self._tasks = [
            asyncio.create_task(runner.run())
            for runner in self.runners
        ]

        try:
            await asyncio.gather(*self._tasks)
        finally:
            self.stop()

    def stop(self) -> None:
        for runner in self.runners:
            runner.stop()

        logger.info("All telemetry runners stopped.")