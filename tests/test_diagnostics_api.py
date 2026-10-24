
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import get_telemetry_query_service
from apps.api.routes.diagnostics import (
    get_anomaly_service,
    router,
)
from apps.api.routes.rag_answer import get_rag_answer_service
from services.rag.llm_client import LLMServiceError


class FakeTelemetryService:
    """Provides deterministic telemetry without connecting to QuestDB."""

    def __init__(self, rows):
        self.rows = rows

    def get_telescope_history(self, telescope_id, limit=100):
        return self.rows[:limit]


class FakeAnomalyService:
    """Flags a measurement when its value exceeds a test threshold."""

    @staticmethod
    def _detect(values):
        flags = [False] * len(values)

        if len(values) < 2:
            return flags

        previous_max = max(values[:-1])

        if values[-1] > max(previous_max, 1e-9) * 2:
            flags[-1] = True

        return flags

    def detect_zscore(self, values):
        return self._detect(values)

    def detect_rolling_zscore(self, values):
        return self._detect(values)


class FakeRAGService:
    def __init__(self, should_fail=False):
        self.calls = []
        self.should_fail = should_fail

    def answer(self, query, limit=5, category=None):
        self.calls.append(query)

        if self.should_fail:
            raise LLMServiceError("Test LLM failure")

        return {
            "query": query,
            "answer": "Check the documented motor operating limits. [S1]",
            "result_count": 1,
            "sources": [
                {
                    "source_id": "S1",
                    "score": 0.9,
                    "chunk_id": "chunk-1",
                    "doc_id": "doc-1",
                    "source_path": "telescope/tracking_and_motor.md",
                    "category": "telescope",
                    "document_title": "Telescope Diagnostics",
                    "section_title": "Motor Temperature",
                    "chunk_index": 0,
                    "content": "Example documented operating guidance.",
                }
            ],
        }


def make_rows(latest_tracking_error=0.1):
    """Returns newest-first telemetry, matching the repository contract."""
    now = datetime.now(timezone.utc)
    rows = []

    tracking_errors = [
        latest_tracking_error,
        0.12,
        0.11,
        0.10,
        0.09,
    ]

    for index, error in enumerate(tracking_errors):
        rows.append(
            {
                "timestamp": now - timedelta(seconds=index),
                "telescope_id": "telescope-01",
                "tracking_error": error,
                "motor_temperature": 25.0,
                "motor_current": 2.0,
                "vibration": 0.1,
                "status": "OK",
            }
        )

    return rows


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)

    yield test_app

    test_app.dependency_overrides.clear()


def configure_dependencies(app, rows, rag_service):
    app.dependency_overrides[get_telemetry_query_service] = (
        lambda: FakeTelemetryService(rows)
    )
    app.dependency_overrides[get_anomaly_service] = (
        lambda: FakeAnomalyService()
    )
    app.dependency_overrides[get_rag_answer_service] = (
        lambda: rag_service
    )


def test_diagnostics_returns_normal_telemetry_without_calling_rag(app):
    rag_service = FakeRAGService()
    configure_dependencies(app, make_rows(), rag_service)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/diagnostics/analyze",
            json={"telescope_id": "telescope-01"},
        )

    assert response.status_code == 200

    body = response.json()
    assert body["telescope_id"] == "telescope-01"
    assert body["is_anomalous"] is False
    assert body["anomalies"] == []
    assert body["explanation"] is None
    assert body["sources"] == []
    assert rag_service.calls == []


def test_diagnostics_detects_latest_anomaly_and_calls_rag(app):
    rag_service = FakeRAGService()
    configure_dependencies(
        app,
        make_rows(latest_tracking_error=8.0),
        rag_service,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/diagnostics/analyze",
            json={"telescope_id": "telescope-01"},
        )

    assert response.status_code == 200

    body = response.json()
    assert body["is_anomalous"] is True
    assert body["latest_telemetry"]["tracking_error"] == 8.0
    assert any(
        item["metric"] == "tracking_error"
        for item in body["anomalies"]
    )
    assert body["explanation"] is not None
    assert body["sources"][0]["source_id"] == "S1"
    assert len(rag_service.calls) == 1


def test_diagnostics_returns_404_when_history_is_empty(app):
    rag_service = FakeRAGService()
    configure_dependencies(app, [], rag_service)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/diagnostics/analyze",
            json={"telescope_id": "missing-telescope"},
        )

    assert response.status_code == 404
    assert "No telemetry found" in response.json()["detail"]
    assert rag_service.calls == []


def test_diagnostics_returns_503_when_rag_llm_is_unavailable(app):
    rag_service = FakeRAGService(should_fail=True)
    configure_dependencies(
        app,
        make_rows(latest_tracking_error=8.0),
        rag_service,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/diagnostics/analyze",
            json={"telescope_id": "telescope-01"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The RAG explanation service is unavailable."
    )
    assert len(rag_service.calls) == 1
