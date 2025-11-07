# Warehouse Knowledge Assistant (LLM-RAG)

Ein produktionsnahes Retrieval-Augmented-Generation (RAG) Referenzprojekt für den Demo-Domain "Warehouse Knowledge Assistant". Der Stack kombiniert FastAPI, Redis Vector Store, Sentence Transformers, Ollama, React/TypeScript, Docker-Compose, Observability (Promtail + Grafana) und Security-Guards, um meine Fähigkeiten als AI Software Engineer abzubilden.

## Architektur auf einen Blick
```mermaid
flowchart LR
    subgraph Frontend
        UI[React Chat UI]
    end
    subgraph Backend
        API[FastAPI Endpoints]
        Guard[Prompt & PII Guards]
        Pipeline[RAG Pipeline]
        Embed[Sentence Transformers]
    end
    subgraph Infra
        Redis[(Redis Vector Store)]
        Ollama[(Ollama LLM)]
        Promtail[(Promtail)]
        Grafana[(Grafana)]
    end

    UI -->|/chat| API --> Guard --> Pipeline --> Ollama
    Pipeline --> Redis
    Pipeline --> Embed
    API -->|Logs| Promtail --> Grafana
```

## Features
- **Backend**: FastAPI mit `/health`, `/ingest`, `/chat`, strukturiertes Logging (structlog), Prometheus-Metriken, Prompt-Injection-Guards, PII-Redaction, Audit-Log.
- **Vector Store**: Redis-Stack (HNSW Index) mit Namespace-Management und automatischem Index-Aufbau.
- **LLM-Orchestrierung**: Sentence-Transformers `all-MiniLM-L6-v2` für Embeddings, Ollama (Default `mistral`, per Request umschaltbar auf `llama3`, `phi3`, `gemma`) inkl. Temperatursteuerung.
- **Frontend**: React + Vite Chat-UI mit Agent-Status, Dark/Light Mode, Quellenanzeige, Retry-/Timeout-Handling.
- **Infra & DevOps**: Docker Compose Stack (FastAPI, Redis, Ollama, Frontend, Promtail, Grafana), Helm Chart Skeleton, GitHub Actions CI, k6 Performance-Skript.
- **Daten & Security**: Seed-Daten (`data/warehouse_faq.md`, `data/warehouse_ops.csv`), Prompt-Guards, Audit-Log, `.env` Handling.

## Repository-Layout
```
backend/   FastAPI Service inkl. Tests & Dockerfile
frontend/  React/Vite Chat Client + Vitest
infra/     Promtail & Grafana Artefakte
charts/    Helm Chart Skeleton für k3s
scripts/   k6 Load-Test Beispiel
docs/      Architektur- & Operations-Dokumente
```

## Setup
### Voraussetzungen
- Python 3.11+
- Node 20 + pnpm (Corepack)
- Docker & Docker Compose (für End-to-End Stack)
- Optional: k6, kubectl, helm

### Lokale Entwicklung
```bash
cp .env.example .env
make install-backend
make install-frontend
```

Seed-Daten laden:
```bash
curl -X POST http://localhost:8000/ingest \
  -H 'Content-Type: application/json' \
  -d '{"documents": [{"path": "data/warehouse_faq.md", "mime_type": "text/markdown"}, {"path": "data/warehouse_ops.csv", "mime_type": "text/csv"}]}'
```

Chat-Aufruf:
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query": "Wie hoch ist der Dock-Durchsatz?"}'
```

### Tests & Qualität
```bash
make test-backend
make test-frontend
make lint
```

### Docker Compose
```bash
docker compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Grafana: `http://localhost:3000` (admin/admin per Default)

### k6 Performance-Test
```bash
k6 run scripts/k6-load.js
```
Ziel: p95 < 1s bei 10 VUs (simuliert ~3M Token/Tag bei Skalierung).

### RAG Smoke-Eval
```bash
./scripts/eval_rag.py --api-base http://localhost:8000
```
Erzeugt Keyword-Hitrates für die enthaltenen Warehouse-Fragen.

### Taskfile (Alternative zu Make)
```bash
task install:backend
task test:frontend
task compose:up
```

### Helm (optional)
```bash
helm install warehouse charts/warehouse-rag --namespace rag --create-namespace
```
Passe `values.yaml` an (Images, Service-Typ, Ressourcen).

## Sicherheit & Observability
- Prompt-Injection-Heuristiken + Blocklist.
- Regex-basierte PII-Maskierung (E-Mail / Telefonnummern).
- Audit-Log (`logs/audit.log`) + Promtail-Scraping → Grafana Dashboard (`infra/grafana-dashboard.json`).
- Prometheus Metriken (`/metrics`): Request-Counter, Retrieval-/LLM-Latenz, Guard-Hits.
- `.env` Workflow, keine Secrets im Repo.

## Dokumentation
- `docs/architecture.md`: Komponenten- & Sequenzdiagramm, Datenfluss.
- `docs/operations.md`: Deploy-, Monitoring- & Cost-Guides.
- `docs/cloud-deployment.md`: Azure Container Apps / AKS Playbook.

## Business Use-Cases
- Warehouse FAQs (Inbound/Outbound KPIs, SOPs)
- Putaway/Picking Priorisierung
- Compliance Checks (PII-Masking, Prompt Guards)
- Agent-Status für Leitstand-Transparenz

## Roadmap / TODOs
- Automatisierte PDF-Ingestion Smoke-Tests
- Alerting Rules für Guard-Hits > Schwelle
- Browser-Plugin (Skeleton vorhanden in Planung)
- Erweiterte Telemetrie via OpenTelemetry Collector
- Augmentiertes Guard-Playbook für mehrsprachige Prompts

## Fit für PRODYNA / AI Software Engineer
- **End-to-End Ownership**: Backend, Frontend, Infra, Observability & CI/CD spiegeln den geforderten Full-Lifecycle-Anspruch wider.
- **Generative KI Patterns**: RAG, Guardrails, Multi-Model-Steuerung, Evaluation-Skript & Performance-Tests demonstrieren praktische Erfahrung.
- **Cloud & DevOps**: Compose, Helm, Azure Playbook, Taskfile und GitHub Actions adressieren Automatisierung & Cloud-Readiness.
- **Collaboration Ready**: Strukturierte Doku, Guard-/Security-Hinweise und Tests erleichtern die Zusammenarbeit mit Data Scientists & Engineers.

Lizenz: [MIT](LICENSE)
