
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routes.rag import get_retriever, router


class FakeRetriever:
    def search(self, query, limit=5, category=None):
        return [
            {
                "score": 0.91,
                "chunk_id": "chunk-1",
                "doc_id": "doc-1",
                "source_path": "telescope/tracking_and_motor.md",
                "category": "telescope",
                "document_title": "Telescope Diagnostics",
                "section_title": "Motor Temperature",
                "chunk_index": 0,
                "content": "Increasing motor temperature may indicate increased load.",
            }
        ]


def test_rag_search_endpoint_returns_sources():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_retriever] = FakeRetriever

    with TestClient(app) as client:
        response = client.post(
            "/rag/search",
            json={
                "query": "Why is the motor overheating?",
                "limit": 3,
                "category": "telescope",
            },
        )

    assert response.status_code == 200

    body = response.json()
    assert body["result_count"] == 1
    assert body["results"][0]["source_path"] == (
        "telescope/tracking_and_motor.md"
    )
    assert body["results"][0]["section_title"] == "Motor Temperature"


def test_rag_search_endpoint_rejects_empty_query():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_retriever] = FakeRetriever

    with TestClient(app) as client:
        response = client.post(
            "/rag/search",
            json={"query": "   "},
        )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_rag_search_endpoint_rejects_missing_query():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_retriever] = FakeRetriever

    with TestClient(app) as client:
        response = client.post(
            "/rag/search",
            json={"limit": 3},
        )

    assert response.status_code == 422
