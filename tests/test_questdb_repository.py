from database.questdb.query_connection import create_query_connection
from database.questdb.repository import QuestDBRepository


def test_get_latest_telescope():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_latest_telescope("TCS-01")

    assert result is not None
    assert result["telescope_id"] == "TCS-01"


def test_get_telescope_history():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_telescope_history(
            "TCS-01",
            limit=10,
        )

    assert len(result) <= 10

    for telemetry in result:
        assert telemetry["telescope_id"] == "TCS-01"


def test_get_latest_camera():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_latest_camera("CCD-01")

    assert result is not None
    assert result["camera_id"] == "CCD-01"


def test_get_camera_history():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_camera_history(
            "CCD-01",
            limit=10,
        )

    assert len(result) <= 10

    for telemetry in result:
        assert telemetry["camera_id"] == "CCD-01"


def test_get_latest_weather():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_latest_weather("WX-01")

    assert result is not None
    assert result["station_id"] == "WX-01"


def test_get_weather_history():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_weather_history(
            "WX-01",
            limit=10,
        )

    assert len(result) <= 10

    for telemetry in result:
        assert telemetry["station_id"] == "WX-01"


def test_get_latest_dome():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_latest_dome("DOME-01")

    assert result is not None
    assert result["dome_id"] == "DOME-01"


def test_get_dome_history():
    with create_query_connection() as connection:
        repository = QuestDBRepository(connection)

        result = repository.get_dome_history(
            "DOME-01",
            limit=10,
        )

    assert len(result) <= 10

    for telemetry in result:
        assert telemetry["dome_id"] == "DOME-01"