
from pathlib import Path

from services.rag.document_loader import MarkdownDocumentLoader


def test_loader_reads_markdown_files(tmp_path: Path):
    telescope_dir = tmp_path / "telescope"
    telescope_dir.mkdir()

    (telescope_dir / "motor.md").write_text(
        "# Motor Diagnostics\n\nCheck temperature and current.",
        encoding="utf-8",
    )

    loader = MarkdownDocumentLoader(tmp_path)
    documents = loader.load()

    assert len(documents) == 1

    document = documents[0]

    assert document.title == "Motor Diagnostics"
    assert document.category == "telescope"
    assert document.source_path == "telescope/motor.md"
    assert "temperature and current" in document.content
    assert document.doc_id


def test_loader_ignores_empty_markdown(tmp_path: Path):
    (tmp_path / "empty.md").write_text(
        "   \n",
        encoding="utf-8",
    )

    documents = MarkdownDocumentLoader(tmp_path).load()

    assert documents == []


def test_loader_returns_empty_list_for_empty_directory(
    tmp_path: Path,
):
    documents = MarkdownDocumentLoader(tmp_path).load()

    assert documents == []


def test_loader_raises_when_directory_missing(tmp_path: Path):
    missing_dir = tmp_path / "missing"

    loader = MarkdownDocumentLoader(missing_dir)

    try:
        loader.load()
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")
