# ADR-0001: Modular Monolith with Async Worker

Date: 2026-03-14

Decision:
Adopt FastAPI modular monolith with Celery worker for async jobs.

Rationale:
- Simplifies deployment and debugging.
- Preserves clear module boundaries without early microservice overhead.

Consequences:
- Need discipline to avoid tight coupling.
