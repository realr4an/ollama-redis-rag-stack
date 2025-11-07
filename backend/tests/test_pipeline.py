import pytest

from app.schemas import ChatRequest
from app.services.embedding import EmbeddingService
from app.services.guards import PIIRedactor, PromptGuard
from app.services.pipeline import RagPipeline


class DummyEmbedding(EmbeddingService):
    def __init__(self):
        pass

    def embed_query(self, text: str):  # type: ignore[override]
        return [0.1] * 4


class DummyVectorStore:
    def similarity_search(self, *, namespace: str, vector, top_k: int):
        return [
            {"id": "doc1", "text": "Warehouse throughput is 220 pallets/h", "score": 0.1},
        ]


class DummyLLM:
    async def generate(self, prompt: str):
        return {"response": "Contact agent@company.com for help"}


@pytest.mark.asyncio
async def test_pipeline_masks_pii():
    pipeline = RagPipeline(
        embedding=DummyEmbedding(),
        vector_store=DummyVectorStore(),
        llm=DummyLLM(),
        guard=PromptGuard(()),
        redactor=PIIRedactor(),
        max_context_chars=400,
    )
    response = await pipeline.chat(ChatRequest(query="What is throughput?"), namespace="demo")
    assert "[REDACTED]" in response.answer
    assert response.sources
