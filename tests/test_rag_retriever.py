
import pytest

from services.rag.retriever import RetrieverService


class FakeEmbedder:
    dimension = 3

    def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class FakeVectorStore:
    def __init__(self):
        self.last_query_vector = None
        self.last_limit = None
        self.last_category = None

    def ensure_collection(self):
        pass

    def search(self, query_vector, limit=5, category=None):
        self.last_query_vector = query_vector
        self.last_limit = limit
        self.last_category = category

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

    def close(self):
        pass


def test_retriever_embeds_query_and_returns_results():
    embedder = FakeEmbedder()
    store = FakeVectorStore()

    retriever = RetrieverService(
        embedder=embedder,
        vector_store=store,
    )

    results = retriever.search(
        query="Why is the motor overheating?",
        limit=3,
        category="telescope",
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert store.last_query_vector == [1.0, 0.0, 0.0]
    assert store.last_limit == 3
    assert store.last_category == "telescope"


def test_retriever_rejects_empty_query():
    retriever = RetrieverService(
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.search("   ")


@pytest.mark.parametrize("limit", [0, 11])
def test_retriever_rejects_invalid_limit(limit):
    retriever = RetrieverService(
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="Limit must be between 1 and 10"):
        retriever.search("motor temperature", limit=limit)
