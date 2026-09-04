# OpsCentreDan Architecture (Initial)

Date: 2026-03-14

## Product Vision
OpsCentreDan is a modular-monolith incident management platform for DevOps/SRE teams with first-class AI-assisted investigation, evidence capture, timeline management, and closeout/COE generation.

## Scope and Constraints
- Production-sensible from day one; avoid toy/demo-only architecture.
- Local-first repeatable bootstrap via Docker Compose.
- Secure-by-default: RBAC, auditability, strict validation, explicit action boundaries for AI.
- Extensible adapter pattern for providers/integrations.
- Vertical slice first, then incremental expansion.

## Major Architectural Decisions
1. Monorepo with mixed runtime
- Decision: Single repo containing Next.js frontend and Python backend/worker.
- Why: Lowest operational and cognitive overhead while preserving module boundaries.
- Tradeoff: Polyglot toolchain complexity (Node + Python).

2. Modular monolith backend (FastAPI)
- Decision: Keep incident, auth, ingestion, AI/RAG, onboarding, and reporting modules in one API service.
- Why: Strong cohesion, simpler deploy/debug path, easier data consistency.
- Tradeoff: Requires discipline to preserve boundaries as codebase grows.

3. Async jobs with Celery + Redis
- Decision: Use Celery workers for ingestion/embedding/background workflows.
- Why: Reliable retries, mature operational model, avoids API blocking.
- Tradeoff: Adds broker + worker service management.

4. PostgreSQL + Qdrant split
- Decision: Store transactional domain data in Postgres and vectors in Qdrant.
- Why: Purpose-fit persistence with clear responsibilities.
- Tradeoff: Dual-storage orchestration and consistency handling.

5. Provider abstraction layer (LLM/Embeddings/Cloud/Observability/Webhooks)
- Decision: Formal interfaces + adapter registration.
- Why: Avoid lock-in and keep incidents decoupled from provider-specific schemas.
- Tradeoff: Slight upfront abstraction cost.

6. Auth model
- Decision: Local auth with JWT and secure password hashing now; OIDC-ready integration seam.
- Why: Enables immediate usability and enterprise upgrade path.
- Tradeoff: Local identity lifecycle management required until SSO enabled.

7. AI safety posture
- Decision: AI endpoints only produce suggestions/drafts; explicit user action required for data mutations.
- Why: Prevents silent unsafe modifications and preserves auditability.
- Tradeoff: Slightly more user clicks.

8. Evidence trust separation
- Decision: Mark every evidence/finding item with provenance (`system`, `human`, `ai_inference`, `ai_retrieved`).
- Why: Maintains evidentiary integrity and avoids inference-fact confusion.
- Tradeoff: Additional metadata handling in UI/API.

## Bounded Contexts
- Identity & Access: users, teams, sessions, roles.
- Incident Core: incidents, lifecycle transitions, owners, tags, relations.
- Incident Collaboration: comments, timeline events, evidence, findings.
- Integrations: inbound connectors, normalized alerts, provider configs.
- Knowledge & RAG: docs ingestion, chunks, embeddings, retrieval.
- Assistant: incident-scoped Q&A, citations, suggested updates.
- Closeout/COE: drafts, action items, approval/finalization.
- Onboarding: setup wizard state and verification checks.
- Audit & Ops: audit events, health checks, job status.

## Data Model (Initial)
Core entities and intent:
- User, Team, TeamMembership
- Incident, IncidentEvent, IncidentComment, EvidenceItem
- AlertEvent (normalized raw payload + extracted fields)
- IntegrationConnector, ProviderConfiguration
- KnowledgeDocument, DocumentChunk, EmbeddingJob
- COEReport, ActionItem
- AuditEvent

Design notes:
- UUID primary keys.
- `created_at`/`updated_at` on all mutable entities.
- Optimistic indexes on incident status/severity/team/updated time.
- JSONB for provider-specific metadata.
- Soft-delete for knowledge docs and provider configs where reasonable.

## Onboarding Flow (Guided Wizard)
1. Admin bootstrap (local account) or configure OIDC placeholder.
2. Workspace setup (org/env/team defaults).
3. Cloud provider metadata config (AWS/Azure/GCP abstraction).
4. Observability provider connector setup.
5. AI provider config + embedding provider config.
6. Knowledge source ingestion kickoff.
7. Connector test webhook.
8. Test incident generation.
9. Readiness checks and completion summary.

## AI/RAG Pipeline
1. Ingestion request created -> queue background job.
2. Fetch document source (file/link/text).
3. Extract text (markdown/plaintext/pdf initial support).
4. Chunk + metadata tagging (source, section, service, env).
5. Embedding provider produces vectors.
6. Upsert vectors to Qdrant collection.
7. Store chunk metadata + job status in Postgres.
8. Retrieval pipeline for assistant:
   - Incident context expansion (service/env/tags/recent activity)
   - Vector search (top-k)
   - Optional lexical fallback from Postgres chunks
   - Response composer with:
     - facts from retrieved evidence
     - clearly separated inference/hypothesis
     - source citations

## Security Model
- Password hashing via Argon2.
- JWT auth with short-lived access tokens.
- RBAC roles: admin, engineer, viewer.
- Endpoint-level authorization checks.
- Input validation with Pydantic everywhere.
- File upload allowlist + size caps.
- Rate limiting on auth/assistant/webhook endpoints.
- Sanitization for rendered markdown/user content.
- Full audit trail for sensitive operations.

## Deployment Model
- Docker Compose services:
  - `web` (Next.js)
  - `api` (FastAPI)
  - `worker` (Celery)
  - `postgres`
  - `redis`
  - `qdrant`
- Health/readiness endpoints and dependency checks.
- Startup bootstrap script:
  - migrate DB
  - initialize vector collection
  - seed admin + demo data
  - verify connectivity

## Key Risks and Practical Mitigations
- Risk: Provider credential misconfiguration.
  - Mitigation: startup validation + onboarding verification checks + explicit error surfaces.
- Risk: AI hallucination presented as fact.
  - Mitigation: strict response schema separating evidence vs inference; citation requirement.
- Risk: ingestion pipeline failures.
  - Mitigation: Celery retries, dead-letter style failure state, job observability.
- Risk: overengineering early.
  - Mitigation: vertical slice first, ADR-driven expansion.

## Verified Reference Baselines (official docs checked)
- Next.js support policy indicates 16.x Active LTS (released Oct 21, 2025); minimum Node.js 20.9 in install docs.
- FastAPI release notes show current changes around 0.120.x line.
- Celery stable user guide documents 5.6.
- SQLAlchemy docs list 2.0.48 current release (as of Mar 2, 2026).
- Alembic docs show 1.18.x line.
- Qdrant GitHub releases list latest as v1.16.3.
- Docker official Postgres image includes 18.x tags; implementation may pin a conservative tested tag.

## Assumptions
- Initial deployment target is local Docker Compose; production guide covers extension.
- LLM/embedding provider keys are optional for boot, required for assistant generation beyond retrieval-only modes.
- Evidence files use local storage in dev, object storage abstraction to be introduced later.
