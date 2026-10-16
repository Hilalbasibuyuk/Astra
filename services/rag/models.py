
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDocument:
    """A complete source document loaded from the knowledge base."""

    doc_id: str
    source_path: str
    category: str
    title: str
    content: str


@dataclass(frozen=True)
class DocumentChunk:
    """A searchable text chunk with its source metadata."""

    chunk_id: str
    doc_id: str
    source_path: str
    category: str
    document_title: str
    section_title: str
    chunk_index: int
    content: str
