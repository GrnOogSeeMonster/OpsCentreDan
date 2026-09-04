# OpsCentreDan Delivery Checklist

Date: 2026-03-14

## Planning and Architecture
- [x] Create `ARCHITECTURE.md`
- [x] Create `PLAN.md`
- [x] Create `TODO.md`
- [x] Create `/docs/architecture.md`
- [x] Create `/docs/api-overview.md`
- [x] Create `/docs/onboarding-flow.md`
- [x] Create `/docs/operations-guide.md`
- [x] Create `/docs/threat-model.md`
- [x] Create ADRs under `/docs/adr/`

## Repository Scaffold
- [x] Create monorepo structure (`apps`, `packages`, `docs`, `infra`, `examples`)
- [x] Scaffold `apps/web` (Next.js + TS)
- [x] Scaffold `apps/api` (FastAPI)
- [x] Scaffold `apps/worker` entrypoint
- [x] Add shared package(s)

## Infrastructure and Runtime
- [x] Add Dockerfiles for web/api/worker
- [x] Add docker compose stack (web/api/worker/postgres/redis/qdrant)
- [x] Add `.env.example`
- [x] Add startup/bootstrap script
- [x] Add health/readiness endpoints
- [x] Add seed/demo flow

## Backend Core
- [x] Config and validation module
- [x] Auth + RBAC (admin/engineer/viewer)
- [x] Incident lifecycle API
- [x] Comments/timeline/evidence API
- [x] Alert ingestion adapter framework
- [x] Connectors CRUD
- [x] Provider config CRUD
- [x] Audit events
- [x] Login hardening (token claims, lockout, refresh rotation, logout revoke)

## AI / RAG
- [x] Knowledge ingestion API
- [x] Async ingestion and embedding jobs
- [x] Chunking + metadata tagging
- [x] Qdrant indexing and retrieval
- [x] Incident-aware assistant API with citations
- [x] Similar incidents retrieval

## Onboarding and UX
- [x] Login page
- [x] Onboarding wizard
- [x] Incident list page
- [x] Incident detail workspace page
- [x] AI panel
- [x] Evidence panel
- [x] Integrations settings page
- [x] Knowledge ingestion status page
- [x] COE editor page

## Closeout / COE
- [x] Draft generation
- [x] Editable report flow
- [x] Finalization flow
- [x] Action items tracking

## Quality and Security
- [x] Input validation and safe rendering
- [x] File upload restrictions
- [x] Rate limiting for sensitive endpoints
- [x] Structured logging
- [x] Unit tests
- [ ] Integration tests
- [x] E2E happy path

## Examples and Seed Data
- [x] Example webhook payloads (Datadog/Prometheus/Grafana/AWS/Azure/GCP/generic)
- [x] Seeded sample incidents
- [x] Seeded sample knowledge docs

## Self-Review Log
- [x] Milestone 1 self-review completed
- [x] Milestone 2 self-review completed
- [x] Milestone 3 self-review completed
