from database.questdb.connection import create_ilp_sender
from services.telemetry.service import TelemetryService
from simulation.telescope.simulator import TelescopeSimulator


def test_telescope_to_questdb_pipeline():

    simulator = TelescopeSimulator("E2E-TCS-01")

    with create_ilp_sender() as sender:

        service = TelemetryService(sender)

        telemetry = simulator.step()

        service.ingest_telescope(telemetry)

        sender.flush()

        assert telemetry.telescope_id == "E2E-TCS-01"