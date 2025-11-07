# Operations Guide

## Deploy-Varianten
1. **Local Dev**: `make install-*`, `uvicorn app.main:app --reload`, `pnpm dev`.
2. **Docker Compose**: `docker compose up --build` (inkl. Redis Stack, Ollama, Grafana, Promtail).
3. **k3s/Helm**: `helm install warehouse charts/warehouse-rag` und Images auf Registry pushen.

## Monitoring & Alerting
- **Metrics**: `/metrics` → scrape via Prometheus. Kennzahlen: `rag_requests_total`, `rag_retrieval_latency_seconds`, `rag_llm_latency_seconds`, `rag_guard_hits_total`.
- **Logs**: JSON-Logs + Audit-Log → Promtail. Beispiel Dashboard (`infra/grafana-dashboard.json`).
- **Alerts (TODO Template)**:
  - Guard-Hits > 5% der Requests (Prompt-Angriffe)
  - p95 Retrieval-Latenz > 1s
  - Fehlende Ingestion-Events > 1h (Daten-Drift)
- **Eval & Regression**: `scripts/eval_rag.py` automatisiert Smoke-Checks gegen definierte Fragen.

## Scaling Guidelines
- **Backend**: Stateless → horizontale Skalierung; Embedding-Model Cache warmhalten.
- **Redis Vector Store**: Nutze Redis Stack Cluster oder Redis Enterprise ab ~5M Chunks.
- **Ollama**: GPU bevorzugt; bei CPU Batch-Größe auf 1 setzen.
- **Frontend**: Static Assets via CDN.

## Cost Controls
- Modellgröße vs. Latenz (llama3 vs. mistral).
- Kontext-Limit `MAX_CONTEXT_CHARS` reduziert Token-Kosten.
- Promtail & Grafana nutzungsabhängig deaktivierbar.

## Betriebs-Checkliste
- [ ] `.env` gepflegt, Secrets via Vault/GitHub Secrets.
- [ ] `docker compose up` erfolgreich + `/health` OK.
- [ ] Seed-Daten ingestiert (`/ingest`).
- [ ] Tests & Lints grün (lokal + CI).
- [ ] Observability Dashboards provisioniert.
- [ ] Taskfile/CI-Pipelines auf Zielumgebung abgestimmt (z.B. Azure Login, Helm Deploy).
