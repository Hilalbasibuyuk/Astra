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