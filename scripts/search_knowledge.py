
from services.rag.embedding import EmbeddingService
from services.rag.vector_store import QdrantVectorStore


def main() -> None:
    embedder = EmbeddingService()
    store = QdrantVectorStore(
        vector_size=embedder.dimension,
    )

    try:
        store.ensure_collection()

        queries = [
            "Why is the telescope motor overheating?",
            "What can cause poor astronomical image quality?",
            "Is the weather suitable for observations?",
            "What should be checked if the dome motor behaves abnormally?",
        ]

        for query in queries:
            print(f"\nQUESTION: {query}")

            query_vector = embedder.embed_query(query)
            results = store.search(query_vector, limit=3)

            for result in results:
                print(f"Score: {result['score']:.4f}")
                print(f"Source: {result['source_path']}")
                print(f"Section: {result['section_title']}")
                print(f"Text: {result['content'][:350]}")
                print("-" * 60)

    finally:
        store.close()


if __name__ == "__main__":
    main()
