
import pytest
from qdrant_client import QdrantClient

from services.rag.models import DocumentChunk
from services.rag.vector_store import QdrantVectorStore


@pytest.fixture
def store():
    client = QdrantClient(":memory:")

    vector_store = QdrantVectorStore(
        collection_name="test_knowledge",
        vector_size=3,
        client=client,
    )
    vector_store.ensure_collection()

    yield vector_store

    vector_store.close()


def make_chunk(
    chunk_id: str = "chunk-1",
    category: str = "telescope",
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        doc_id="doc-1",
        source_path="telescope/test.md",
        category=category,
        document_title="Test Telescope Guide",
        section_title="Motor Temperature",
        chunk_index=0,
        content="Increasing motor temperature can indicate increased load.",
    )


def test_collection_is_created(store):
    collections = store.client.get_collections().collections

    assert any(
        collection.name == "test_knowledge"
        for collection in collections
    )


def test_upsert_and_search(store):
    chunk = make_chunk()
    vector = [1.0, 0.0, 0.0]

    count = store.upsert_chunks([chunk], [vector])

    assert count == 1

    results = store.search(
        query_vector=[1.0, 0.0, 0.0],
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["source_path"] == "telescope/test.md"
    assert results[0]["section_title"] == "Motor Temperature"


def test_search_can_filter_by_category(store):
    telescope_chunk = make_chunk("chunk-1", "telescope")
    camera_chunk = make_chunk("chunk-2", "camera")

    store.upsert_chunks(
        [telescope_chunk, camera_chunk],
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
    )

    results = store.search(
        query_vector=[1.0, 0.0, 0.0],
        limit=5,
        category="camera",
    )

    assert len(results) == 1
    assert results[0]["category"] == "camera"


def test_upsert_rejects_mismatched_counts(store):
    with pytest.raises(ValueError):
        store.upsert_chunks(
            [make_chunk()],
            [],
        )


def test_search_rejects_wrong_vector_dimension(store):
    with pytest.raises(ValueError):
        store.search(query_vector=[1.0, 0.0], limit=1)
