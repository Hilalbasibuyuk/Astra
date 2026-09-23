from datetime import datetime

from pydantic import BaseModel, Field


class TelescopeTelemetry(BaseModel):
    timestamp: datetime

    telescope_id: str = Field(min_length=1)

    azimuth: float
    elevation: float

    right_ascension: float
    declination: float

    tracking_error: float = Field(ge=0)

    motor_temperature: float
    motor_current: float = Field(ge=0)

    vibration: float = Field(ge=0)

    status: str

class CameraTelemetry(BaseModel):
    timestamp: datetime
    camera_id: str = Field(min_length=1)
    sensor_temperature: float
    exposure_time: float = Field(gt=0)
    gain: float = Field(ge=0)
    frame_rate: float = Field(ge=0)
    image_quality: float = Field(ge=0, le=1)
    status: str

class WeatherTelemetry(BaseModel):
    timestamp: datetime
    station_id: str = Field(min_length=1)
    temperature: float
    humidity: float = Field(ge=0, le=100)
    pressure: float = Field(gt=0)
    wind_speed: float = Field(ge=0)
    seeing: float = Field(ge=0)
    cloud_cover: float = Field(ge=0, le=1)
    status: str

class DomeTelemetry(BaseModel):
    timestamp: datetime
    dome_id: str = Field(min_length=1)
    azimuth: float
    rotation_speed: float = Field(ge=0)
    shutter_open: bool
    motor_temperature: float
    status: str