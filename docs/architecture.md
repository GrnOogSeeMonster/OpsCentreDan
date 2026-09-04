# Architecture

See top-level [ARCHITECTURE.md](../ARCHITECTURE.md) for the full initial design narrative.

## Runtime Topology
- `apps/web`: Next.js UX workspace
- `apps/api`: FastAPI modular monolith
- `apps/worker`: Celery worker process (runs from API image)
- PostgreSQL: transactional store
- Redis: broker/cache/rate support
- Qdrant: vector retrieval

## Core Patterns
- Adapter interfaces for connectors/providers
- Explicit provenance model on evidence/comments
- Human-in-the-loop for AI-generated changes
- Async ingestion and indexing workflows
