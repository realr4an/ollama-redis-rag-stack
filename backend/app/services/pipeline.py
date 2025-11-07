from __future__ import annotations

import structlog
from time import perf_counter
from typing import Any

from ..instrumentation import (
    LLM_LATENCY,
    MODEL_USAGE_COUNTER,
    PROMPT_GUARD_COUNTER,
    REQUEST_COUNTER,
    RETRIEVAL_LATENCY,
)
from ..schemas import ChatRequest, ChatResponse, SourceChunk
from .embedding import EmbeddingService
from .guards import PIIRedactor, PromptGuard
from .ollama import OllamaClient
from .vector_store import RedisVectorStore

logger = structlog.get_logger(__name__)


class RagPipeline:
    def __init__(
        self,
        *,
        embedding: EmbeddingService,
        vector_store: RedisVectorStore,
        llm: OllamaClient,
        guard: PromptGuard,
        redactor: PIIRedactor,
        max_context_chars: int,
    ) -> None:
        self.embedding = embedding
        self.vector_store = vector_store
        self.llm = llm
        self.guard = guard
        self.redactor = redactor
        self.max_context_chars = max_context_chars

    async def chat(
        self,
        request: ChatRequest,
        namespace: str,
        *,
        model: str,
        temperature: float,
    ) -> ChatResponse:
        guard_level = request.guard_level or "standard"
        guard_result = self.guard.check(request.query, guard_level)
        if not guard_result.allowed:
            PROMPT_GUARD_COUNTER.labels(action="blocked").inc()
            REQUEST_COUNTER.labels(status="guard_block").inc()
            logger.warning("guard_block", reasons=guard_result.reasons)
            return ChatResponse(
                answer="Your query was blocked by the safety system.",
                sources=[],
                guard_tripped=True,
                stats={"reasons": guard_result.reasons},
            )

        start_retrieval = perf_counter()
        query_vector = self.embedding.embed_query(request.query)
        chunks = self.vector_store.similarity_search(
            namespace=namespace, vector=query_vector, top_k=request.top_k or 4
        )
        RETRIEVAL_LATENCY.observe(perf_counter() - start_retrieval)

        prompt = self._build_prompt(request.query, chunks)
        start_llm = perf_counter()
        try:
            llm_payload = await self.llm.generate(prompt, model=model, temperature=temperature)
        except TimeoutError:
            REQUEST_COUNTER.labels(status="llm_timeout").inc()
            raise
        except Exception:
            REQUEST_COUNTER.labels(status="llm_error").inc()
            raise
        LLM_LATENCY.observe(perf_counter() - start_llm)
        REQUEST_COUNTER.labels(status="success").inc()
        MODEL_USAGE_COUNTER.labels(model=model).inc()

        answer = llm_payload.get("response") or llm_payload.get("message", {}).get("content", "")
        redacted_answer = self.redactor.redact(answer)

        sources = [
            SourceChunk(
                document_id=chunk["id"],
                score=chunk.get("score", 0.0),
                text=chunk["text"],
                metadata=chunk.get("metadata"),
            )
            for chunk in chunks
        ]

        return ChatResponse(
            answer=redacted_answer.strip(),
            sources=sources,
            guard_tripped=False,
            stats={
                "tokens_context": len(prompt) // 4,
                "prompt_guard": guard_result.reasons,
                "model": model,
            },
        )

    def _build_prompt(self, question: str, chunks: list[dict[str, Any]]) -> str:
        context = []
        total_chars = 0
        for idx, chunk in enumerate(chunks, start=1):
            snippet = chunk["text"]
            if total_chars + len(snippet) > self.max_context_chars:
                snippet = snippet[: self.max_context_chars - total_chars]
            context.append(f"Source {idx}: {snippet}")
            total_chars += len(snippet)
            if total_chars >= self.max_context_chars:
                break
        context_block = "\n---\n".join(context)
        return (
            "You are a Warehouse Knowledge Assistant for logistics supervisors.\n"
            "Use only the provided sources. If unsure, answer with 'I do not know'.\n"
            f"Sources:\n{context_block}\n"
            f"Question: {question}\n"
            "Respond with concise bullet points and cite source numbers like [S1]."
        )
