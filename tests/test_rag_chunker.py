
from services.rag.chunker import MarkdownChunker
from services.rag.models import SourceDocument


def make_document(content: str) -> SourceDocument:
    return SourceDocument(
        doc_id="test-document",
        source_path="telescope/test.md",
        category="telescope",
        title="Test Document",
        content=content,
    )


def test_chunker_preserves_section_titles():
    document = make_document(
        "# Telescope Diagnostics\n\n"
        "General diagnostic introduction.\n\n"
        "## Motor Temperature\n\n"
        "Check the motor temperature and current.\n\n"
        "## Tracking Error\n\n"
        "Compare desired and measured positions."
    )

    chunks = MarkdownChunker().split_document(document)

    titles = [chunk.section_title for chunk in chunks]

    assert "Motor Temperature" in titles
    assert "Tracking Error" in titles


def test_chunker_preserves_source_metadata():
    document = make_document(
        "# Test Document\n\n"
        "Check motor temperature and current."
    )

    chunks = MarkdownChunker().split_document(document)

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.doc_id == document.doc_id
    assert chunk.source_path == document.source_path
    assert chunk.category == document.category
    assert chunk.document_title == document.title
    assert chunk.chunk_index == 0
    assert chunk.chunk_id


def test_chunker_respects_maximum_size():
    document = make_document(
        "# Long Section\n\n"
        + ("Motor temperature must be monitored carefully. " * 100)
    )

    chunker = MarkdownChunker(max_chars=200, overlap=30)
    chunks = chunker.split_document(document)

    assert len(chunks) > 1
    assert all(len(chunk.content) <= 200 for chunk in chunks)


def test_chunker_rejects_invalid_configuration():
    try:
        MarkdownChunker(max_chars=100, overlap=100)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_chunker_produces_stable_chunk_ids():
    document = make_document(
        "# Diagnostics\n\nCheck temperature and motor current."
    )

    chunker = MarkdownChunker()

    first = chunker.split_document(document)
    second = chunker.split_document(document)

    assert [chunk.chunk_id for chunk in first] == [
        chunk.chunk_id for chunk in second
    ]
