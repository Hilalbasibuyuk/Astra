from database.questdb.repository import QuestDBRepository


class TelemetryQueryService:
    def __init__(self, repository: QuestDBRepository):
        self.repository = repository

    # ------------------------------------------------------------------
    # Telescope
    # ------------------------------------------------------------------

    def get_latest_telescope(
        self,
        telescope_id: str,
    ):
        return self.repository.get_latest_telescope(
            telescope_id
        )

    def get_telescope_history(
        self,
        telescope_id: str,
        limit: int = 100,
    ):
        return self.repository.get_telescope_history(
            telescope_id,
            limit,
        )

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def get_latest_camera(
        self,
        camera_id: str,
    ):
        return self.repository.get_latest_camera(
            camera_id
        )

    def get_camera_history(
        self,
        camera_id: str,
        limit: int = 100,
    ):
        return self.repository.get_camera_history(
            camera_id,
            limit,
        )

    # ------------------------------------------------------------------
    # Weather
    # ------------------------------------------------------------------

    def get_latest_weather(
        self,
        station_id: str,
    ):
        return self.repository.get_latest_weather(
            station_id
        )

    def get_weather_history(
        self,
        station_id: str,
        limit: int = 100,
    ):
        return self.repository.get_weather_history(
            station_id,
            limit,
        )

    # ------------------------------------------------------------------
    # Dome
    # ------------------------------------------------------------------

    def get_latest_dome(
        self,
        dome_id: str,
    ):
        return self.repository.get_latest_dome(
            dome_id
        )

    def get_dome_history(
        self,
        dome_id: str,
        limit: int = 100,
    ):
        return self.repository.get_dome_history(
            dome_id,
            limit,
        )