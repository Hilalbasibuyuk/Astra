
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from services.rag.models import DocumentChunk


class QdrantVectorStore:
    """Stores and retrieves ASTRA knowledge chunks."""

    
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "astra_knowledge",
        vector_size: int = 384,
        client: QdrantClient | None = None,
    ):
        self.client = client or QdrantClient(url=url)
        self.collection_name = collection_name
        self.vector_size = vector_size


    def ensure_collection(self) -> None:
        collections = self.client.get_collections().collections

        exists = any(
            collection.name == self.collection_name
            for collection in collections
        )

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            return

        info = self.client.get_collection(self.collection_name)
        existing_size = info.config.params.vectors.size

        if existing_size != self.vector_size:
            raise ValueError(
                f"Collection '{self.collection_name}' uses vector size "
                f"{existing_size}; expected {self.vector_size}. "
                "Use a new collection when changing embedding models."
            )

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> int:
        if len(chunks) != len(vectors):
            raise ValueError(
                "The number of chunks must match the number of vectors"
            )

        if not chunks:
            return 0

        points = []

        for chunk, vector in zip(chunks, vectors):
            if len(vector) != self.vector_size:
                raise ValueError(
                    f"Expected vector dimension {self.vector_size}, "
                    f"got {len(vector)}"
                )

            # Qdrant point IDs must be integers or UUIDs.
            point_id = str(
                uuid5(NAMESPACE_URL, chunk.chunk_id)
            )

            payload = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "source_path": chunk.source_path,
                "category": chunk.category,
                "document_title": chunk.document_title,
                "section_title": chunk.section_title,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        return len(points)

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        category: str | None = None,
    ) -> list[dict]:
        if limit < 1:
            raise ValueError("limit must be at least 1")

        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Expected query vector dimension {self.vector_size}, "
                f"got {len(query_vector)}"
            )

        query_filter = None

        if category:
            from qdrant_client.http.models import (
                FieldCondition,
                Filter,
                MatchValue,
            )

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category),
                    )
                ]
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        results = []

        for point in response.points:
            results.append(
                {
                    "score": point.score,
                    **(point.payload or {}),
                }
            )

        return results

    def close(self) -> None:
        self.client.close()
