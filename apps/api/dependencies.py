from database.questdb.query_connection import (
    create_query_connection,
)
from database.questdb.repository import QuestDBRepository
from services.telemetry.query_service import TelemetryQueryService


def get_questdb_repository():
    with create_query_connection() as connection:
        yield QuestDBRepository(connection)


def get_telemetry_query_service():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)
        yield TelemetryQueryService(repository)