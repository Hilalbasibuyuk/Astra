from datetime import datetime, timezone

from questdb.ingress import Sender

from database.questdb.connection import create_ilp_sender


def send_telescope_telemetry(
    sender: Sender,
    telescope_id: str,
    azimuth: float,
    elevation: float,
    right_ascension: float,
    declination: float,
    tracking_error: float,
    motor_temperature: float,
    motor_current: float,
    vibration: float,
    status: str,
) -> None:

    timestamp = datetime.now(timezone.utc)

    sender.row(
        "telescope_telemetry",
        symbols={
            "telescope_id": telescope_id,
            "status": status,
        },
        columns={
            "azimuth": azimuth,
            "elevation": elevation,
            "right_ascension": right_ascension,
            "declination": declination,
            "tracking_error": tracking_error,
            "motor_temperature": motor_temperature,
            "motor_current": motor_current,
            "vibration": vibration,
        },
        at=timestamp,
    )

def send_camera_telemetry(
    sender: Sender,
    camera_id: str,
    sensor_temperature: float,
    exposure_time: float,
    gain: float,
    frame_rate: float,
    image_quality: float,
    status: str,
) -> None:
    timestamp = datetime.now(timezone.utc)
    sender.row(
        "camera_telemetry",
        symbols={
            "camera_id": camera_id,
            "status": status,
        },
        columns={
            "sensor_temperature": sensor_temperature,
            "exposure_time": exposure_time,
            "gain": gain,
            "frame_rate": frame_rate,
            "image_quality": image_quality,
        },
        at=timestamp,
    )


def send_weather_telemetry(
    sender: Sender,
    station_id: str,
    temperature: float,
    humidity: float,
    pressure: float,
    wind_speed: float,
    seeing: float,
    cloud_cover: float,
    status: str,
) -> None:
    timestamp = datetime.now(timezone.utc)
    sender.row(
        "weather_telemetry",
        symbols={
            "station_id": station_id,
            "status": status,
        },
        columns={
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "seeing": seeing,
            "cloud_cover": cloud_cover,
        },
        at=timestamp,
    )


def send_dome_telemetry(
    sender: Sender,
    dome_id: str,
    azimuth: float,
    rotation_speed: float,
    shutter_open: bool,
    motor_temperature: float,
    status: str,
) -> None:
    timestamp = datetime.now(timezone.utc)
    sender.row(
        "dome_telemetry",
        symbols={
            "dome_id": dome_id,
            "status": status,
        },
        columns={
            "azimuth": azimuth,
            "rotation_speed": rotation_speed,
            "shutter_open": shutter_open,
            "motor_temperature": motor_temperature,
        },
        at=timestamp,
    )