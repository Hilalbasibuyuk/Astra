
from services.rag.embedding import EmbeddingService
from services.rag.vector_store import QdrantVectorStore


class RetrieverService:
    """Coordinates query embedding and vector retrieval."""

    def __init__(
        self,
        embedder: EmbeddingService | None = None,
        vector_store: QdrantVectorStore | None = None,
    ):
        self.embedder = embedder or EmbeddingService()

        self.vector_store = vector_store or QdrantVectorStore(
            vector_size=self.embedder.dimension,
        )

        # Fail early if the collection is missing or misconfigured.
        self.vector_store.ensure_collection()

    def search(
        self,
        query: str,
        limit: int = 5,
        category: str | None = None,
    ) -> list[dict]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Query cannot be empty")

        if not 1 <= limit <= 10:
            raise ValueError("Limit must be between 1 and 10")

        query_vector = self.embedder.embed_query(normalized_query)

        return self.vector_store.search(
            query_vector=query_vector,
            limit=limit,
            category=category,
        )

    def close(self) -> None:
        self.vector_store.close()
