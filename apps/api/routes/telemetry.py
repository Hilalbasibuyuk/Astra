from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.dependencies import get_telemetry_query_service
from services.telemetry.query_service import TelemetryQueryService
from services.telemetry.schemas import (
    CameraTelemetryResponse,
    DomeTelemetryResponse,
    TelescopeTelemetryResponse,
    WeatherTelemetryResponse,
)


router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
)


# ======================================================================
# Telescope
# ======================================================================

@router.get(
    "/telescope/{telescope_id}/latest",
    response_model=TelescopeTelemetryResponse,
)
def get_latest_telescope_telemetry(
    telescope_id: str,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    result = service.get_latest_telescope(
        telescope_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Telescope telemetry not found",
        )

    return result


@router.get(
    "/telescope/{telescope_id}/history",
    response_model=list[TelescopeTelemetryResponse],
)
def get_telescope_history(
    telescope_id: str,
    limit: Annotated[
        int,
        Query(ge=1, le=1000),
    ] = 100,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    return service.get_telescope_history(
        telescope_id,
        limit,
    )


# ======================================================================
# Camera
# ======================================================================

@router.get(
    "/camera/{camera_id}/latest",
    response_model=CameraTelemetryResponse,
)
def get_latest_camera_telemetry(
    camera_id: str,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    result = service.get_latest_camera(
        camera_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Camera telemetry not found",
        )

    return result


@router.get(
    "/camera/{camera_id}/history",
    response_model=list[CameraTelemetryResponse],
)
def get_camera_history(
    camera_id: str,
    limit: Annotated[
        int,
        Query(ge=1, le=1000),
    ] = 100,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    return service.get_camera_history(
        camera_id,
        limit,
    )


# ======================================================================
# Weather
# ======================================================================

@router.get(
    "/weather/{station_id}/latest",
    response_model=WeatherTelemetryResponse,
)
def get_latest_weather_telemetry(
    station_id: str,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    result = service.get_latest_weather(
        station_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Weather telemetry not found",
        )

    return result


@router.get(
    "/weather/{station_id}/history",
    response_model=list[WeatherTelemetryResponse],
)
def get_weather_history(
    station_id: str,
    limit: Annotated[
        int,
        Query(ge=1, le=1000),
    ] = 100,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    return service.get_weather_history(
        station_id,
        limit,
    )


# ======================================================================
# Dome
# ======================================================================

@router.get(
    "/dome/{dome_id}/latest",
    response_model=DomeTelemetryResponse,
)
def get_latest_dome_telemetry(
    dome_id: str,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    result = service.get_latest_dome(
        dome_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dome telemetry not found",
        )

    return result


@router.get(
    "/dome/{dome_id}/history",
    response_model=list[DomeTelemetryResponse],
)
def get_dome_history(
    dome_id: str,
    limit: Annotated[
        int,
        Query(ge=1, le=1000),
    ] = 100,
    service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
):
    return service.get_dome_history(
        dome_id,
        limit,
    )