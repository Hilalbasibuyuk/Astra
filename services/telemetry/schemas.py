from datetime import datetime

from pydantic import BaseModel


class TelescopeTelemetryResponse(BaseModel):
    timestamp: datetime
    telescope_id: str
    azimuth: float
    elevation: float
    right_ascension: float
    declination: float
    tracking_error: float
    motor_temperature: float
    motor_current: float
    vibration: float
    status: str


class CameraTelemetryResponse(BaseModel):
    timestamp: datetime
    camera_id: str
    sensor_temperature: float
    exposure_time: float
    gain: float
    frame_rate: float
    image_quality: float
    status: str

class WeatherTelemetryResponse(BaseModel):
    timestamp: datetime
    station_id: str
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    seeing: float
    cloud_cover: float
    status: str

class DomeTelemetryResponse(BaseModel):
    timestamp: datetime
    dome_id: str
    azimuth: float
    rotation_speed: float
    shutter_open: bool
    motor_temperature: float
    status: str