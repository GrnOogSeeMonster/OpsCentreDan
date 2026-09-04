# OpsCentreDan

An AI-assisted incident management platform for DevOps/SRE teams: alerts arrive by
webhook, become incidents with a timeline and evidence trail, an assistant answers
questions against an ingested knowledge base with citations, and the incident closes
out into an editable Correction-of-Error report.

---

## Status

**The most complete project in this collection.** Every layer of the vertical slice is
implemented — ingest, incident lifecycle, RAG assistant, COE closeout. Last worked on
14 March 2026.

| | |
|---|---|
| Size | ~4,200 lines across a FastAPI backend and a Next.js frontend |
| API | 9 route modules, all implemented — auth, incidents, webhooks, knowledge, assistant, reports, integrations, onboarding, health |
| Domain model | 313 lines of SQLAlchemy entities, one Alembic baseline migration |
| RAG | Chunking, pluggable embedding providers, Qdrant vector store, retrieval service with citation and inference markers |
| Web | 7 pages — login, onboarding, incidents list, incident workspace, report editor, knowledge, connector settings |
| Async | Celery worker running from the API image |
| Tests | 4 pytest modules (auth security, chunking, webhook adapters) plus an e2e smoke script. **Integration tests were not written** |
| Docs | ARCHITECTURE, PLAN, TODO, 5 topic docs, 3 ADRs, a threat model |
| Verified | Not re-run recently. The compose stack defines postgres, redis, qdrant, api, worker and web; treat the walkthrough below as the intended path, not a fresh test result |

The one open item on `TODO.md` is integration tests. Everything else on that checklist
is ticked, and the ticks match what is in the tree.

Note: this directory is **not under git** — there is no `.git` here and no remote.

---

## Capabilities

- incident lifecycle operations
- inbound alert ingestion adapters
- AI-assisted incident investigation with citations
- asynchronous knowledge ingestion and vector retrieval
- evidence capture and timeline history
- COE/closeout report drafting and finalization

## Repo Structure

- `apps/web` - Next.js frontend workspace
- `apps/api` - FastAPI backend API + domain logic
- `apps/worker` - worker process entrypoint (uses API code)
- `docs` - architecture, operations, threat model, ADRs
- `infra` - Dockerfiles and scripts
- `examples` - webhook payloads and sample knowledge docs

## Quick Start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open:
- Web app: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Readiness: `http://localhost:8000/ready`

## Seeded Credentials

- Email: `admin@opscentredan.dev`
- Password: `ChangeMeNow123!`

## First Vertical Slice Walkthrough

1. Login from `/login`.
2. Open `/incidents` and create or select an incident.
3. Add comments/evidence and review timeline.
4. Ask AI assistant in incident panel.
5. Generate a draft COE report and edit/finalize it.
6. Use `/onboarding` and `/settings/connectors` to configure providers and connectors.

## Inbound Webhook Test

A seeded connector is created during bootstrap:
- Name: `Generic Demo Webhook`
- Secret: `demo-secret`

Use payload example at `examples/webhook-payloads/generic.json`.

## Notes on AI/RAG

- Knowledge docs can be ingested from `/knowledge`.
- Embeddings and assistant generation require `OPENAI_API_KEY`.
- Without API key, assistant and embedding paths fail loudly with clear API errors.

## Security Posture (Current)

- JWT auth + RBAC (admin, engineer, viewer)
- Audit events for sensitive operations
- Input validation via Pydantic
- File upload type and size restrictions
- Rate limiting on auth/webhook/assistant endpoints
- Provenance markers on comments/evidence (`human`, `system`, `ai_inference`, `ai_retrieved`)

## Development

### API local

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web local

```bash
npm install
npm --workspace apps/web run dev
```

## Documentation

- `ARCHITECTURE.md`
- `PLAN.md`
- `TODO.md`
- `docs/architecture.md`
- `docs/api-overview.md`
- `docs/onboarding-flow.md`
- `docs/operations-guide.md`
- `docs/threat-model.md`
- `docs/adr/*`
