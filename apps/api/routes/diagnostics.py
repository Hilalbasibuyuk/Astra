from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.dependencies import get_telemetry_query_service
from apps.api.routes.rag_answer import get_rag_answer_service
from services.anomaly_detection.service import AnomalyDetectionService
from services.rag.generator import RAGAnswerService
from services.rag.llm_client import LLMServiceError
from services.telemetry.query_service import TelemetryQueryService
from services.diagnostics.service import TelescopeDiagnosticsService


router = APIRouter(
    prefix="/api/v1/diagnostics",
    tags=["diagnostics"],
)


class TelescopeDiagnosticsRequest(BaseModel):
    telescope_id: str = Field(min_length=1, max_length=100)
    history_limit: int = Field(default=100, ge=2, le=1000)
    rag_limit: int = Field(default=5, ge=1, le=10)


@lru_cache(maxsize=1)
def get_anomaly_service() -> AnomalyDetectionService:
    return AnomalyDetectionService()


@router.post("/analyze")
def analyze_telescope(
    request: TelescopeDiagnosticsRequest,
    telemetry_service: TelemetryQueryService = Depends(
        get_telemetry_query_service
    ),
    anomaly_service: AnomalyDetectionService = Depends(
        get_anomaly_service
    ),
    rag_service: RAGAnswerService = Depends(
        get_rag_answer_service
    ),
) -> dict[str, Any]:
    service = TelescopeDiagnosticsService(
        telemetry_service=telemetry_service,
        anomaly_service=anomaly_service,
        rag_service=rag_service,
    )

    try:
        return service.analyze(
            telescope_id=request.telescope_id,
            history_limit=request.history_limit,
            rag_limit=request.rag_limit,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="The RAG explanation service is unavailable.",
        ) from exc