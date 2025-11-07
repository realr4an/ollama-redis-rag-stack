from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    redis: bool
    model: str


class IngestDocument(BaseModel):
    id: str | None = None
    text: str | None = None
    path: str | None = None
    metadata: dict[str, Any] | None = None
    mime_type: str | None = Field(default=None, description="text/markdown, text/csv, application/pdf")

    @model_validator(mode="after")
    def validate_source(self) -> "IngestDocument":
        if not self.text and not self.path:
            raise ValueError("Either text or path must be provided")
        return self


class IngestRequest(BaseModel):
    namespace: str | None = None
    documents: list[IngestDocument]


class IngestResponse(BaseModel):
    ingested: int
    namespace: str


class SourceChunk(BaseModel):
    document_id: str
    score: float
    text: str
    metadata: dict[str, Any] | None = None


class ChatRequest(BaseModel):
    query: str
    namespace: str | None = None
    top_k: int | None = None
    guard_level: str | None = Field(default="standard", description="standard|strict|disabled")


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    guard_tripped: bool = False
    stats: dict[str, Any] = Field(default_factory=dict)


class AuditRecord(BaseModel):
    query: str
    response: str
    guard_tripped: bool
    namespace: str
    sources: list[dict[str, Any]]
