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
    def __init__(self):
        self.called_with: dict[str, str | float] = {}

    async def generate(self, prompt: str, model: str | None = None, temperature: float | None = None):
        self.called_with = {"model": model or "", "temperature": temperature or 0.0}
        return {"response": "Contact agent@company.com for help"}


@pytest.mark.asyncio
async def test_pipeline_masks_pii():
    llm = DummyLLM()
    pipeline = RagPipeline(
        embedding=DummyEmbedding(),
        vector_store=DummyVectorStore(),
        llm=llm,
        guard=PromptGuard(()),
        redactor=PIIRedactor(),
        max_context_chars=400,
    )
    response = await pipeline.chat(
        ChatRequest(query="What is throughput?"),
        namespace="demo",
        model="mistral",
        temperature=0.2,
    )
    assert "[REDACTED]" in response.answer
    assert response.sources
    assert llm.called_with["model"] == "mistral"
