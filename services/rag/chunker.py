
import hashlib
import re

from services.rag.models import DocumentChunk, SourceDocument


class MarkdownChunker:
    """Splits Markdown documents into searchable chunks."""

    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

    def __init__(
        self,
        max_chars: int = 1200,
        overlap: int = 150,
    ):
        if max_chars <= 0:
            raise ValueError("max_chars must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= max_chars:
            raise ValueError("overlap must be smaller than max_chars")

        self.max_chars = max_chars
        self.overlap = overlap

    def split_document(
        self,
        document: SourceDocument,
    ) -> list[DocumentChunk]:
        sections = self._extract_sections(document.content)
        chunks: list[DocumentChunk] = []

        for section_title, section_text in sections:
            for content in self._split_text(section_text):
                normalized = content.strip()

                if not normalized:
                    continue

                chunk_index = len(chunks)

                # Stable for the same document, section, index and text.
                identity = (
                    f"{document.doc_id}|{section_title}|"
                    f"{chunk_index}|{normalized}"
                )
                chunk_id = hashlib.sha256(
                    identity.encode("utf-8")
                ).hexdigest()[:20]

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=document.doc_id,
                        source_path=document.source_path,
                        category=document.category,
                        document_title=document.title,
                        section_title=section_title,
                        chunk_index=chunk_index,
                        content=normalized,
                    )
                )

        return chunks

    def split_documents(
        self,
        documents: list[SourceDocument],
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        for document in documents:
            chunks.extend(self.split_document(document))

        return chunks

    def _extract_sections(
        self,
        content: str,
    ) -> list[tuple[str, str]]:
        sections: list[tuple[str, str]] = []
        current_title = "Introduction"
        current_lines: list[str] = []

        for line in content.splitlines():
            match = self.HEADING_PATTERN.match(line.strip())

            if match:
                self._append_section(
                    sections,
                    current_title,
                    current_lines,
                )

                current_title = match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        self._append_section(
            sections,
            current_title,
            current_lines,
        )

        return sections

    @staticmethod
    def _append_section(
        sections: list[tuple[str, str]],
        title: str,
        lines: list[str],
    ) -> None:
        text = "\n".join(lines).strip()

        if text:
            sections.append((title, text))

    def _split_text(self, text: str) -> list[str]:
        if len(text) <= self.max_chars:
            return [text] if text.strip() else []

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            # A single paragraph may be longer than max_chars.
            if len(paragraph) > self.max_chars:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.extend(self._split_long_text(paragraph))
                continue

            candidate = (
                f"{current}\n\n{paragraph}" if current else paragraph
            )

            if len(candidate) <= self.max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)

                # Carry a small tail forward to preserve local context.
                overlap_text = (
                    current[-self.overlap:] if self.overlap else ""
                )

                current = (
                    f"{overlap_text}\n\n{paragraph}"
                    if overlap_text
                    else paragraph
                )

                # The overlap plus next paragraph may exceed the limit.
                if len(current) > self.max_chars:
                    chunks.extend(self._split_long_text(current))
                    current = ""

        if current:
            chunks.append(current)

        return chunks

    def _split_long_text(self, text: str) -> list[str]:
        """Split oversized paragraphs into character windows."""
        chunks: list[str] = []
        start = 0
        step = self.max_chars - self.overlap

        while start < len(text):
            end = min(start + self.max_chars, len(text))
            piece = text[start:end].strip()

            if piece:
                chunks.append(piece)

            if end == len(text):
                break

            start += step

        return chunks
