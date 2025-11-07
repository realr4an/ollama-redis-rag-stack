from __future__ import annotations

import csv
import uuid
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from ..schemas import IngestDocument


class DocumentParser:
    def __init__(self, base_path: Path | None = None):
        self.base_path = (base_path or Path.cwd()).resolve()

    def load(self, doc: IngestDocument) -> str:
        if doc.text:
            return doc.text
        if not doc.path:
            raise ValueError("Document missing both text and path")

        provided_path = Path(doc.path)
        if provided_path.is_absolute():
            file_path = provided_path
        else:
            relative_parts = provided_path.parts
            if relative_parts and relative_parts[0] == self.base_path.name:
                relative_parts = relative_parts[1:]
            file_path = self.base_path.joinpath(*relative_parts)
        file_path = file_path.resolve()
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        mime = doc.mime_type or file_path.suffix.lower()
        if mime in {"text/markdown", ".md", "md"}:
            return file_path.read_text(encoding="utf-8")
        if mime in {"text/csv", ".csv", "csv"}:
            return self._read_csv(file_path)
        if mime in {"application/pdf", ".pdf", "pdf"}:
            return self._read_pdf(file_path)
        return file_path.read_text(encoding="utf-8")

    def _read_csv(self, path: Path) -> str:
        rows: list[str] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(", ".join(f"{k}={v}" for k, v in row.items()))
        return "\n".join(rows)

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)


class Chunker:
    def __init__(self, chunk_size: int = 600, overlap: int = 80) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        length = len(text)
        while start < length:
            end = min(length, start + self.chunk_size)
            chunks.append(text[start:end])
            if end == length:
                break
            start = max(0, end - self.overlap)
        return [chunk.strip() for chunk in chunks if chunk.strip()]


class IngestionService:
    def __init__(self, parser: DocumentParser, chunker: Chunker):
        self.parser = parser
        self.chunker = chunker

    def prepare(self, doc: IngestDocument) -> list[dict]:
        text = self.parser.load(doc)
        doc_id = doc.id or str(uuid.uuid4())
        chunks = self.chunker.split(text)
        payloads = []
        for idx, chunk in enumerate(chunks):
            payloads.append(
                {
                    "id": f"{doc_id}:{idx}",
                    "text": chunk,
                    "metadata": doc.metadata or {},
                }
            )
        return payloads
