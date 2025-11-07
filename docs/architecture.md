# Architektur

## Komponenten
- **FastAPI Backend**: Endpunkte `/health`, `/ingest`, `/chat`, Instrumentierung, Guards.
- **RAG Pipeline**: SentenceTransformer Embeddings → Redis Vector Store Retrieval → Guarding → Ollama Generation.
- **Frontend**: React Chat UI mit Agent-Status, Theme Toggle, Quellenanzeige.
- **Observability**: structlog JSON Logs → Promtail → Grafana; Prometheus-Metriken direkt aus FastAPI.
- **Infrastructure**: Docker Compose Stack, optional Helm Deployment.

## Sequenzdiagramm
```mermaid
sequenceDiagram
    participant FE as React Client
    participant API as FastAPI
    participant Guard as Prompt Guard
    participant VS as Redis Vector Store
    participant LLM as Ollama

    FE->>API: POST /chat (query)
    API->>Guard: run_checks()
    Guard-->>API: allowed?
    API->>VS: similarity_search(query_embed)
    VS-->>API: ranked chunks
    API->>LLM: prompt(context+question)
    LLM-->>API: answer
    API->>FE: response + sources + stats
```

## Datenfluss
1. **Ingestion**: Parser (Markdown/CSV/PDF) → Chunker → Embedding → Redis HNSW Index.
2. **Retrieval**: Query → Embedding → Vector Similarity (KNN) → Context Kürzung (max chars).
3. **LLM Prompting**: System Prompt + Quellen + Frage, Guard-Feedback, PII-Redaction.
4. **Observability**: structlog JSON, Guard-Hits, Prometheus Latenzen, Audit-Logs.

## Quality Gates
- Pytest + Vitest
- Ruff + Black + ESLint + Prettier
- GitHub Actions (Lint, Tests, Docker Build)
- k6 Performance Baseline
