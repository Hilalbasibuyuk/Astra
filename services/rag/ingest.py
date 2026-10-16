
from services.rag.chunker import MarkdownChunker
from services.rag.document_loader import MarkdownDocumentLoader
from services.rag.embedding import EmbeddingService
from services.rag.vector_store import QdrantVectorStore


def index_knowledge_base() -> int:
    loader = MarkdownDocumentLoader()
    chunker = MarkdownChunker()
    embedder = EmbeddingService()

    store = QdrantVectorStore(
        vector_size=embedder.dimension,
    )

    try:
        store.ensure_collection()

        documents = loader.load()
        chunks = chunker.split_documents(documents)

        if not chunks:
            print("No document chunks found.")
            return 0

        vectors = embedder.embed_documents(
            [chunk.content for chunk in chunks]
        )

        indexed_count = store.upsert_chunks(chunks, vectors)

        print(f"Documents loaded: {len(documents)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Chunks indexed: {indexed_count}")

        return indexed_count

    finally:
        store.close()


if __name__ == "__main__":
    index_knowledge_base()
