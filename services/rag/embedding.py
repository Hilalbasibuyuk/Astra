
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Creates vectors for document passages and user queries."""

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small",
    ):
        self.model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        prefixed_texts = [
            f"passage: {text}" for text in texts
        ]

        vectors = self.model.encode(
            prefixed_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        vector = self.model.encode(
            [f"query: {query.strip()}"],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )[0]

        return vector.tolist()
