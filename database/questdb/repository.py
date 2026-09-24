from typing import Any


class QuestDBRepository:
    def __init__(self, connection):
        self.connection = connection

    # ------------------------------------------------------------------
    # Telescope
    # ------------------------------------------------------------------

    def get_latest_telescope(
        self,
        telescope_id: str,
    ) -> dict[str, Any] | None:

        query = """
            SELECT
                timestamp,
                telescope_id,
                azimuth,
                elevation,
                right_ascension,
                declination,
                tracking_error,
                motor_temperature,
                motor_current,
                vibration,
                status
            FROM telescope_telemetry
            WHERE telescope_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (telescope_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "timestamp",
            "telescope_id",
            "azimuth",
            "elevation",
            "right_ascension",
            "declination",
            "tracking_error",
            "motor_temperature",
            "motor_current",
            "vibration",
            "status",
        ]

        return dict(zip(columns, row))

    def get_telescope_history(
        self,
        telescope_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        query = """
            SELECT
                timestamp,
                telescope_id,
                azimuth,
                elevation,
                right_ascension,
                declination,
                tracking_error,
                motor_temperature,
                motor_current,
                vibration,
                status
            FROM telescope_telemetry
            WHERE telescope_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (telescope_id, limit),
            )
            rows = cursor.fetchall()

        columns = [
            "timestamp",
            "telescope_id",
            "azimuth",
            "elevation",
            "right_ascension",
            "declination",
            "tracking_error",
            "motor_temperature",
            "motor_current",
            "vibration",
            "status",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def get_latest_camera(
        self,
        camera_id: str,
    ) -> dict[str, Any] | None:

        query = """
            SELECT
                timestamp,
                camera_id,
                sensor_temperature,
                exposure_time,
                gain,
                frame_rate,
                image_quality,
                status
            FROM camera_telemetry
            WHERE camera_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (camera_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "timestamp",
            "camera_id",
            "sensor_temperature",
            "exposure_time",
            "gain",
            "frame_rate",
            "image_quality",
            "status",
        ]

        return dict(zip(columns, row))

    def get_camera_history(
        self,
        camera_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        query = """
            SELECT
                timestamp,
                camera_id,
                sensor_temperature,
                exposure_time,
                gain,
                frame_rate,
                image_quality,
                status
            FROM camera_telemetry
            WHERE camera_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (camera_id, limit),
            )
            rows = cursor.fetchall()

        columns = [
            "timestamp",
            "camera_id",
            "sensor_temperature",
            "exposure_time",
            "gain",
            "frame_rate",
            "image_quality",
            "status",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Weather
    # ------------------------------------------------------------------

    def get_latest_weather(
        self,
        station_id: str,
    ) -> dict[str, Any] | None:

        query = """
            SELECT
                timestamp,
                station_id,
                temperature,
                humidity,
                pressure,
                wind_speed,
                seeing,
                cloud_cover,
                status
            FROM weather_telemetry
            WHERE station_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (station_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "timestamp",
            "station_id",
            "temperature",
            "humidity",
            "pressure",
            "wind_speed",
            "seeing",
            "cloud_cover",
            "status",
        ]

        return dict(zip(columns, row))

    def get_weather_history(
        self,
        station_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        query = """
            SELECT
                timestamp,
                station_id,
                temperature,
                humidity,
                pressure,
                wind_speed,
                seeing,
                cloud_cover,
                status
            FROM weather_telemetry
            WHERE station_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (station_id, limit),
            )
            rows = cursor.fetchall()

        columns = [
            "timestamp",
            "station_id",
            "temperature",
            "humidity",
            "pressure",
            "wind_speed",
            "seeing",
            "cloud_cover",
            "status",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Dome
    # ------------------------------------------------------------------

    def get_latest_dome(
        self,
        dome_id: str,
    ) -> dict[str, Any] | None:

        query = """
            SELECT
                timestamp,
                dome_id,
                azimuth,
                rotation_speed,
                shutter_open,
                motor_temperature,
                status
            FROM dome_telemetry
            WHERE dome_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (dome_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "timestamp",
            "dome_id",
            "azimuth",
            "rotation_speed",
            "shutter_open",
            "motor_temperature",
            "status",
        ]

        return dict(zip(columns, row))

    def get_dome_history(
        self,
        dome_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        query = """
            SELECT
                timestamp,
                dome_id,
                azimuth,
                rotation_speed,
                shutter_open,
                motor_temperature,
                status
            FROM dome_telemetry
            WHERE dome_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (dome_id, limit),
            )
            rows = cursor.fetchall()

        columns = [
            "timestamp",
            "dome_id",
            "azimuth",
            "rotation_speed",
            "shutter_open",
            "motor_temperature",
            "status",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]