from datetime import datetime, timedelta, timezone

import pytest

from services.diagnostics.service import TelescopeDiagnosticsService


class FakeTelemetryService:
    def __init__(self, rows):
        self.rows = rows

    def get_telescope_history(self, telescope_id, limit=100):
        return self.rows[:limit]


class FakeRAGService:
    def __init__(self):
        self.calls = []

    def answer(self, query, limit=5, category=None):
        self.calls.append(query)
        return {
            "query": query,
            "answer": "The sources describe relevant operating checks. [S1]",
            "result_count": 1,
            "sources": [
                {
                    "source_id": "S1",
                    "score": 0.9,
                    "chunk_id": "chunk-1",
                    "doc_id": "doc-1",
                    "source_path": "docs/telescope.md",
                    "category": "telescope",
                    "document_title": "Telescope Operations",
                    "section_title": "Motor checks",
                    "chunk_index": 0,
                    "content": "Example reference content",
                }
            ],
        }


def make_rows():
    now = datetime.now(timezone.utc)
    rows = []

    # Mostly stable measurements, followed by a large tracking error.
    tracking_errors = [0.10, 0.11, 0.09, 0.10, 0.12, 0.11, 8.0]

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

    # Repository history is newest-first.
    return rows


def test_analysis_returns_latest_telemetry_and_metrics():
    service = TelescopeDiagnosticsService(
        telemetry_service=FakeTelemetryService(make_rows()),
        rag_service=FakeRAGService(),
    )

    result = service.analyze("telescope-01")

    assert result["telescope_id"] == "telescope-01"
    assert result["observations_used"] == 7
    assert result["latest_telemetry"]["tracking_error"] == 0.10
    assert "tracking_error" in result["metrics"]


def test_empty_history_raises_lookup_error():
    service = TelescopeDiagnosticsService(
        telemetry_service=FakeTelemetryService([]),
    )

    with pytest.raises(LookupError):
        service.analyze("missing-telescope")


def test_rag_is_called_only_when_latest_metric_is_anomalous():
    rag = FakeRAGService()
    service = TelescopeDiagnosticsService(
        telemetry_service=FakeTelemetryService(make_rows()),
        rag_service=rag,
    )

    result = service.analyze("telescope-01")

    # The latest row is the oldest timestamp after reversing the history;
    # it is deliberately normal in this fixture.
    assert result["is_anomalous"] is False
    assert rag.calls == []