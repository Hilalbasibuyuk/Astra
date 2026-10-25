
import asyncio
import logging

from database.questdb.connection import create_ilp_sender
from services.anomaly_detection.telemetry_monitor import (
    TelemetryAnomalyMonitor,
)
from services.telemetry.multi_runner import MultiTelemetryRunner
from services.telemetry.runner import TelemetryRunner
from services.telemetry.service import TelemetryService
from simulation.telescope.simulator import TelescopeSimulator
from simulation.camera.simulator import CameraSimulator
from simulation.weather.simulator import WeatherSimulator
from simulation.dome.simulator import DomeSimulator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting ASTRA telemetry worker")

    with create_ilp_sender() as sender:
        telemetry_service = TelemetryService(sender)
        anomaly_monitor = TelemetryAnomalyMonitor()

        telescope_runner = TelemetryRunner(
            simulator=TelescopeSimulator("TCS-01"),
            telemetry_service=telemetry_service,
            interval=1.0,
            anomaly_monitor=anomaly_monitor,
        )

        camera_runner = TelemetryRunner(
            simulator=CameraSimulator("CCD-01"),
            telemetry_service=telemetry_service,
            interval=1.0,
            anomaly_monitor=anomaly_monitor,
        )

        weather_runner = TelemetryRunner(
            simulator=WeatherSimulator("WX-01"),
            telemetry_service=telemetry_service,
            interval=1.0,
            anomaly_monitor=anomaly_monitor,
        )

        dome_runner = TelemetryRunner(
            simulator=DomeSimulator("DOME-01"),
            telemetry_service=telemetry_service,
            interval=1.0,
            anomaly_monitor=anomaly_monitor,
        )

        multi_runner = MultiTelemetryRunner(
            runners=[
                telescope_runner,
                camera_runner,
                weather_runner,
                dome_runner,
            ]
        )

        try:
            await multi_runner.run()

        except KeyboardInterrupt:
            logger.info("Telemetry worker interrupted")

        finally:
            multi_runner.stop()
            logger.info("ASTRA telemetry worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
