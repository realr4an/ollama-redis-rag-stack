from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import redis
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .config import Settings, get_settings
from .logging_config import configure_logging
from .schemas import AuditRecord, ChatRequest, ChatResponse, HealthResponse, IngestRequest, IngestResponse
from .services.audit import AuditTrail
from .services.embedding import EmbeddingService
from .services.guards import PIIRedactor, PromptGuard
from .services.ingestion import Chunker, DocumentParser, IngestionService
from .services.ollama import OllamaClient
from .services.pipeline import RagPipeline
from .services.vector_store import RedisVectorStore

logger = structlog.get_logger(__name__)


def get_pipeline(request: Request) -> RagPipeline:
    return request.app.state.pipeline


def get_settings_dependency() -> Settings:  # pragma: no cover - tiny wrapper
    return get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("starting_app", env=settings.environment)

    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=False,
    )
    vector_store = RedisVectorStore(
        redis_client,
        index_name=settings.redis_index_name,
        dim=settings.embedding_dimension,
    )
    vector_store.ensure_index()

    embedding_service = EmbeddingService(settings.embedding_model)
    ingestion_service = IngestionService(
        parser=DocumentParser(base_path=Path(settings.data_path)),
        chunker=Chunker(),
    )
    ollama_client = OllamaClient(
        base_url=settings.ollama_host,
        model=settings.ollama_model,
        timeout=settings.ollama_timeout,
    )
    guard = PromptGuard(settings.guard_blocklist)
    redactor = PIIRedactor(settings.pii_mask_token)
    pipeline = RagPipeline(
        embedding=embedding_service,
        vector_store=vector_store,
        llm=ollama_client,
        guard=guard,
        redactor=redactor,
        max_context_chars=settings.max_context_tokens,
    )
    audit_trail = AuditTrail(Path("logs/audit.log"))

    app.state.redis = redis_client
    app.state.vector_store = vector_store
    app.state.embedding = embedding_service
    app.state.ingestion_service = ingestion_service
    app.state.pipeline = pipeline
    app.state.audit = audit_trail
    app.state.settings = settings

    try:
        yield
    finally:
        await ollama_client.aclose()
        redis_client.close()
        logger.info("shutdown_complete")


app = FastAPI(title="Warehouse Knowledge Assistant", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings_dependency)) -> HealthResponse:
    redis_ok = False
    try:
        redis_ok = bool(app.state.redis.ping())
    except Exception:  # pragma: no cover - best effort
        redis_ok = False
    return HealthResponse(redis=redis_ok, model=settings.ollama_model)


@app.post("/ingest", response_model=IngestResponse)
def ingest(
    payload: IngestRequest,
    request: Request,
    settings: Settings = Depends(get_settings_dependency),
) -> IngestResponse:
    namespace = payload.namespace or settings.ingestion_namespace
    ingestion_service: IngestionService = request.app.state.ingestion_service
    embedding: EmbeddingService = request.app.state.embedding
    vector_store: RedisVectorStore = request.app.state.vector_store

    prepared: list[dict] = []
    for doc in payload.documents:
        prepared.extend(ingestion_service.prepare(doc))
    embeddings = embedding.embed([chunk["text"] for chunk in prepared])
    for chunk, vector in zip(prepared, embeddings):
        chunk["embedding"] = vector
    count = vector_store.upsert(namespace=namespace, documents=prepared)
    logger.info("ingested", count=count, namespace=namespace)
    return IngestResponse(ingested=count, namespace=namespace)


@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    pipeline: RagPipeline = Depends(get_pipeline),
    settings: Settings = Depends(get_settings_dependency),
) -> ChatResponse:
    namespace = payload.namespace or settings.ingestion_namespace
    model = payload.model or settings.ollama_model
    if model not in settings.ollama_allowed_models:
        raise HTTPException(status_code=400, detail="Unsupported model requested")
    temperature = payload.temperature if payload.temperature is not None else settings.ollama_temperature
    try:
        response = await pipeline.chat(payload, namespace, model=model, temperature=temperature)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="LLM generation timed out")
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    audit: AuditTrail = request.app.state.audit
    audit.write(
        AuditRecord(
            query=payload.query,
            response=response.answer,
            guard_tripped=response.guard_tripped,
            namespace=namespace,
            sources=[source.model_dump() for source in response.sources],
        )
    )
    return response


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
