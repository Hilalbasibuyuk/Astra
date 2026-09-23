from database.questdb.connection import create_ilp_sender
from services.telemetry.service import TelemetryService
from simulation.camera.simulator import CameraSimulator
from simulation.weather.simulator import WeatherSimulator
from simulation.dome.simulator import DomeSimulator


def test_camera_telemetry_pipeline():
    simulator = CameraSimulator("E2E-CCD-01")

    with create_ilp_sender() as sender:
        service = TelemetryService(sender)

        telemetry = simulator.step()
        service.ingest_camera(telemetry)

        sender.flush()
def test_weather_telemetry_pipeline():
    simulator = WeatherSimulator("E2E-WX-01")

    with create_ilp_sender() as sender:
        service = TelemetryService(sender)

        telemetry = simulator.step()
        service.ingest_weather(telemetry)

        sender.flush()

def test_dome_telemetry_pipeline():
    simulator = DomeSimulator("E2E-DOME-01")

    with create_ilp_sender() as sender:
        service = TelemetryService(sender)

        telemetry = simulator.step()
        service.ingest_dome(telemetry)

        sender.flush()

