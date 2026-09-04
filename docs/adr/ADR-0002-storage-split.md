# ADR-0002: Postgres + Qdrant Persistence Split

Date: 2026-03-14

Decision:
Use Postgres for transactional entities and Qdrant for vector retrieval.

Rationale:
- Strong fit for incident domain + RAG retrieval workloads.

Consequences:
- Dual-database operations require stronger observability and sync handling.
