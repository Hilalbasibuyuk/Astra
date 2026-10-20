
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routes.rag_answer import (
    get_rag_answer_service,
    router,
)


class FakeAnswerService:
    def answer(self, query, limit=5, category=None):
        return {
            "query": query,
            "answer": "The motor may be under increased load. [S1]",
            "result_count": 1,
            "sources": [
                {
                    "source_id": "S1",
                    "score": 0.91,
                    "chunk_id": "chunk-1",
                    "doc_id": "doc-1",
                    "source_path": "telescope/tracking_and_motor.md",
                    "category": "telescope",
                    "document_title": "Telescope Diagnostics",
                    "section_title": "Motor Temperature",
                    "chunk_index": 0,
                    "content": (
                        "Increasing motor temperature may indicate "
                        "increased load."
                    ),
                }
            ],
        }


def create_test_client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_rag_answer_service] = FakeAnswerService
    return TestClient(app)


def test_answer_endpoint_returns_answer_and_sources():
    with create_test_client() as client:
        response = client.post(
            "/rag/answer",
            json={
                "query": "Why is the motor overheating?",
                "limit": 3,
                "category": "telescope",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["result_count"] == 1
    assert "[S1]" in body["answer"]
    assert body["sources"][0]["source_id"] == "S1"


def test_answer_endpoint_rejects_whitespace_query():
    with create_test_client() as client:
        response = client.post(
            "/rag/answer",
            json={"query": "   "},
        )

    assert response.status_code == 422


def test_answer_endpoint_rejects_missing_query():
    with create_test_client() as client:
        response = client.post(
            "/rag/answer",
            json={"limit": 3},
        )

    assert response.status_code == 422
