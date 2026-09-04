from __future__ import annotations

import json
from dataclasses import dataclass

from qdrant_client.http import models as qmodels
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import DocumentChunk, Incident, IncidentComment, IncidentEvent, KnowledgeDocument
from app.rag.chunking import summarize_evidence_snippets
from app.rag.providers import get_embedding_provider, get_llm_provider
from app.rag.vector_store import VectorStore


@dataclass
class RetrievalItem:
    chunk_id: str
    source_type: str
    source_ref: str
    excerpt: str
    score: float


class RagService:
    def __init__(self) -> None:
        self.embedding_provider = get_embedding_provider()
        self.llm_provider = get_llm_provider()
        self.vector_store = VectorStore()

    async def retrieve(self, question: str, incident: Incident, limit: int = 8) -> list[RetrievalItem]:
        vectors = await self.embedding_provider.embed_texts([question])
        if not vectors:
            return []
        hits = self.vector_store.search(vectors[0], limit=limit)

        items: list[RetrievalItem] = []
        for hit in hits:
            payload = hit.payload or {}
            if payload.get("environment") not in {incident.environment, "*", None, ""}:
                continue
            items.append(
                RetrievalItem(
                    chunk_id=str(payload.get("chunk_id", "")),
                    source_type=str(payload.get("source_type", "knowledge")),
                    source_ref=str(payload.get("source_ref", "")),
                    excerpt=str(payload.get("content", ""))[:500],
                    score=float(hit.score or 0.0),
                )
            )
        return items

    async def answer_incident_question(
        self,
        db: AsyncSession,
        incident_id: str,
        question: str,
    ) -> dict:
        incident = (
            await db.execute(select(Incident).where(Incident.id == incident_id))
        ).scalar_one_or_none()
        if not incident:
            raise ValueError("Incident not found")

        recent_events = (
            await db.execute(
                select(IncidentEvent)
                .where(IncidentEvent.incident_id == incident_id)
                .order_by(IncidentEvent.created_at.desc())
                .limit(8)
            )
        ).scalars().all()
        recent_comments = (
            await db.execute(
                select(IncidentComment)
                .where(IncidentComment.incident_id == incident_id)
                .order_by(IncidentComment.created_at.desc())
                .limit(6)
            )
        ).scalars().all()

        retrieved = await self.retrieve(question=question, incident=incident)

        context_blob = {
            "incident": {
                "id": incident.id,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "environment": incident.environment,
                "tags": incident.tags,
                "affected_systems": incident.affected_systems,
            },
            "recent_events": [
                {"type": e.event_type, "message": e.message, "ts": e.created_at.isoformat()} for e in recent_events
            ],
            "recent_comments": [
                {"body": c.body[:500], "provenance": c.provenance.value} for c in recent_comments
            ],
            "retrieved_sources": [
                {
                    "chunk_id": r.chunk_id,
                    "source_ref": r.source_ref,
                    "source_type": r.source_type,
                    "score": r.score,
                    "excerpt": r.excerpt,
                }
                for r in retrieved
            ],
            "task": "Answer the question using evidence. Output strict JSON with keys: answer, evidence_summary, inferences, uncertainty, suggested_next_actions.",
            "question": question,
        }

        prompt = json.dumps(context_blob, ensure_ascii=True)
        raw_answer = await self.llm_provider.answer(prompt)

        try:
            parsed = json.loads(raw_answer)
        except json.JSONDecodeError:
            parsed = {
                "answer": raw_answer,
                "evidence_summary": summarize_evidence_snippets([r.excerpt for r in retrieved]),
                "inferences": ["Model returned non-JSON output; treat suggestions as draft."],
                "uncertainty": "medium",
                "suggested_next_actions": ["Verify hypothesis against live logs and metrics."],
            }

        parsed["citations"] = [
            {
                "source_type": r.source_type,
                "source_ref": r.source_ref,
                "chunk_id": r.chunk_id,
                "excerpt": r.excerpt,
                "score": round(r.score, 4),
            }
            for r in retrieved
        ]
        return parsed


async def get_similar_incidents(db: AsyncSession, incident: Incident, limit: int = 5) -> list[dict]:
    rows = (
        await db.execute(
            select(Incident)
            .where(Incident.id != incident.id)
            .where(Incident.environment == incident.environment)
            .order_by(Incident.updated_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [
        {
            "incident_id": row.id,
            "title": row.title,
            "status": row.status.value,
            "severity": row.severity.value,
            "updated_at": row.updated_at.isoformat(),
        }
        for row in rows
    ]
