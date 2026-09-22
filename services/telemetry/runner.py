import asyncio
import logging

from services.telemetry.service import TelemetryService
from simulation.telescope.simulator import TelescopeSimulator


logger = logging.getLogger(__name__)


class TelemetryRunner:

    def __init__(
        self,
        simulator: TelescopeSimulator,
        telemetry_service: TelemetryService,
        interval: float = 1.0,
    ):
        self.simulator = simulator
        self.telemetry_service = telemetry_service
        self.interval = interval

        self._running = False

    async def run(self) -> None:
        self._running = True

        logger.info(
            "Telemetry runner started for %s",
            self.simulator.telescope_id,
        )

        while self._running:

            telemetry = self.simulator.step()

            self.telemetry_service.ingest_telescope(
                telemetry
            )

            logger.info(
                "Telemetry generated: telescope=%s temperature=%.2f",
                telemetry.telescope_id,
                telemetry.motor_temperature,
            )

            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self._running = False

        logger.info(
            "Telemetry runner stopped for %s",
            self.simulator.telescope_id,
        )