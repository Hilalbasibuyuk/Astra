import asyncio
import logging

from services.telemetry.service import TelemetryService

logger = logging.getLogger(__name__)


class TelemetryRunner:
    def __init__(
        self,
        simulator,
        telemetry_service: TelemetryService,
        interval: float = 1.0,
        scenario_engine=None,
    ):
        self.simulator = simulator
        self.telemetry_service = telemetry_service
        self.interval = interval
        self.scenario_engine = scenario_engine
        self._running = False

    async def run(self) -> None:
        self._running = True

        logger.info(
            "Telemetry runner started for %s",
            self.simulator.__class__.__name__,
        )

        while self._running:
            telemetry = self.simulator.step()

            if self.scenario_engine is not None:
                telemetry = self.scenario_engine.apply(
                    telemetry
                )

            self.telemetry_service.ingest(telemetry)

            logger.info(
                "Telemetry generated: type=%s",
                type(telemetry).__name__,
            )

            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self._running = False

        logger.info(
            "Telemetry runner stopped for %s",
            self.simulator.__class__.__name__,
        )