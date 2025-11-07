from pathlib import Path

from app.schemas import IngestDocument
from app.services.ingestion import Chunker, DocumentParser, IngestionService


def test_document_parser_reads_markdown(tmp_path: Path):
    md_file = tmp_path / "doc.md"
    md_file.write_text("# Title\nHello", encoding="utf-8")
    parser = DocumentParser(base_path=tmp_path)
    doc = IngestDocument(path="doc.md", mime_type="text/markdown")
    assert "Hello" in parser.load(doc)


def test_chunker_splits_text():
    chunker = Chunker(chunk_size=10, overlap=2)
    text = "ABCDEFGHIJKLMNO"
    chunks = chunker.split(text)
    assert len(chunks) >= 2


def test_ingestion_service_creates_chunks(tmp_path: Path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("Sample text for ingestion", encoding="utf-8")
    service = IngestionService(DocumentParser(base_path=tmp_path), Chunker(chunk_size=8, overlap=1))
    prepared = service.prepare(IngestDocument(path="doc.md", mime_type="text/markdown"))
    assert prepared
    assert prepared[0]["text"].strip()
