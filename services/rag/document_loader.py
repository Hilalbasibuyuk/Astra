
import hashlib
from pathlib import Path

from services.rag.models import SourceDocument


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


class MarkdownDocumentLoader:
    """Loads Markdown documents from the ASTRA knowledge directory."""

    def __init__(self, knowledge_dir: Path | str | None = None):
        self.knowledge_dir = Path(
            knowledge_dir or DEFAULT_KNOWLEDGE_DIR
        ).resolve()

    def load(self) -> list[SourceDocument]:
        if not self.knowledge_dir.exists():
            raise FileNotFoundError(
                f"Knowledge directory not found: {self.knowledge_dir}"
            )

        if not self.knowledge_dir.is_dir():
            raise NotADirectoryError(
                f"Knowledge path is not a directory: {self.knowledge_dir}"
            )

        documents: list[SourceDocument] = []

        for path in sorted(self.knowledge_dir.rglob("*.md")):
            content = path.read_text(encoding="utf-8").strip()

            # Ignore empty Markdown files.
            if not content:
                continue

            relative_path = path.relative_to(
                self.knowledge_dir
            ).as_posix()

            category = path.parent.name
            title = self._extract_title(content)

            # Stable ID: the same relative source path gets the same ID.
            doc_id = hashlib.sha256(
                relative_path.encode("utf-8")
            ).hexdigest()[:16]

            documents.append(
                SourceDocument(
                    doc_id=doc_id,
                    source_path=relative_path,
                    category=category,
                    title=title,
                    content=content,
                )
            )

        return documents

    @staticmethod
    def _extract_title(content: str) -> str:
        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("# "):
                return stripped[2:].strip()

        return "Untitled Document"
