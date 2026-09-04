# OpsCentreDan Implementation Plan

Date: 2026-03-14

## Delivery Strategy
Ship a working vertical slice first, then expand safely while preserving production-sensible architecture.

## Phase 1 - Discovery and Design
- [x] Define architecture and bounded contexts.
- [x] Define initial data model and entity responsibilities.
- [x] Define onboarding and setup flow.
- [x] Define AI/RAG ingestion and retrieval pipeline.
- [x] Define security baseline and deployment strategy.
- [x] Document decisions and assumptions.

## Phase 2 - Scaffold and Runtime Foundation
- [ ] Create monorepo directories and workspace configuration.
- [ ] Scaffold Next.js frontend with TypeScript and baseline UI shell.
- [ ] Scaffold FastAPI backend with modular package layout.
- [ ] Scaffold Celery worker entrypoint.
- [ ] Add Dockerfiles and compose stack.
- [ ] Add `.env.example` and config validation.
- [ ] Add DB models, Alembic baseline migration, and health/readiness endpoints.

## Phase 3 - Core Incident Domain Vertical Slice
- [ ] Implement auth (local login, JWT, RBAC guards).
- [ ] Implement incident CRUD and lifecycle transitions.
- [ ] Implement comments, timeline events, evidence metadata.
- [ ] Implement normalized alert event model.
- [ ] Implement webhook ingest endpoint with adapter routing.
- [ ] Build UI pages: login, incident list, incident workspace detail.
- [ ] Seed demo users/incidents and verify end-to-end incident workflow.

## Phase 4 - AI/RAG Foundation
- [ ] Implement knowledge documents and ingestion jobs.
- [ ] Implement chunking and metadata tagging.
- [ ] Implement embedding abstraction and provider adapters.
- [ ] Implement Qdrant indexing and retrieval service.
- [ ] Implement incident-scoped assistant API with citations + inference markers.
- [ ] Build UI assistant panel for Q&A and suggested updates.

## Phase 5 - Onboarding and Provider Setup
- [ ] Implement wizard flow backend state and validation checks.
- [ ] Implement web onboarding wizard UI.
- [ ] Implement provider configuration endpoints/screens (cloud/observability/AI).
- [ ] Implement first connector test + first incident generation test from wizard.

## Phase 6 - Closeout / COE
- [ ] Implement COE report draft generation endpoint.
- [ ] Implement editable report model and finalize flow.
- [ ] Implement action items with owners and due dates.
- [ ] Build closeout editor UI.

## Phase 7 - Hardening and Documentation
- [ ] Add unit tests for core domain logic.
- [ ] Add integration tests for critical API paths.
- [ ] Add one e2e happy path (alert -> incident -> assistant -> closeout draft).
- [ ] Add structured logging and error handling polish.
- [ ] Complete docs set in `/docs` including ADRs and threat model.
- [ ] Ensure compose bootstrap reliability and startup checks.

## Milestone Reviews
After each major milestone:
- Security review (authz, validation, injection surfaces, secret handling).
- Maintainability review (module boundaries, complexity, naming, docs).
- Complexity review (remove premature abstractions).

## Definition of Done (for this implementation cycle)
- Local `docker compose up` produces a usable stack.
- User can login, ingest alert, manage incident, add evidence/comments.
- User can query assistant and receive cited responses with uncertainty markers.
- User can generate/edit/finalize COE report draft.
- Docs and examples are complete enough for follow-on development.
