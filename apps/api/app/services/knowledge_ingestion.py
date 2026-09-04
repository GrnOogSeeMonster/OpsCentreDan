from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from qdrant_client.http import models as qmodels
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import DocumentChunk, EmbeddingJob, EmbeddingJobStatus, KnowledgeDocument
from app.rag.chunking import chunk_text
from app.rag.providers import get_embedding_provider
from app.rag.vector_store import VectorStore


async def enqueue_embedding_job(db: AsyncSession, document_id: str) -> EmbeddingJob:
    job = EmbeddingJob(document_id=document_id, status=EmbeddingJobStatus.PENDING)
    db.add(job)
    await db.flush()
    return job


def extract_text_for_document(document: KnowledgeDocument) -> str:
    if document.source_type in {"text", "markdown"}:
        return document.text_content

    if document.source_type == "file" and document.source_ref:
        path = Path(document.source_ref)
        if not path.exists():
            raise FileNotFoundError(f"File source not found: {document.source_ref}")
        if path.suffix.lower() in {".txt", ".md", ".log"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".pdf":
            from PyPDF2 import PdfReader

            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
    return document.text_content


async def process_embedding_job(db: AsyncSession, job_id: str) -> None:
    job = (await db.execute(select(EmbeddingJob).where(EmbeddingJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise ValueError("Embedding job not found")

    document = (
        await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == job.document_id))
    ).scalar_one_or_none()
    if not document:
        raise ValueError("Knowledge document not found")

    job.status = EmbeddingJobStatus.RUNNING
    job.started_at = datetime.utcnow()
    job.attempts += 1

    text = extract_text_for_document(document)
    chunks = chunk_text(text)

    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))

    embedding_provider = get_embedding_provider()
    vectors = await embedding_provider.embed_texts(chunks) if chunks else []

    vector_store = VectorStore()
    if vectors:
        vector_store.ensure_collection(vector_size=len(vectors[0]))

    points: list[qmodels.PointStruct] = []
    for index, chunk in enumerate(chunks):
        vector_id = str(uuid4())
        chunk_id = str(uuid4())
        row = DocumentChunk(
            id=chunk_id,
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            metadata_json=document.metadata_json,
            vector_id=vector_id,
        )
        db.add(row)

        if vectors:
            points.append(
                qmodels.PointStruct(
                    id=vector_id,
                    vector=vectors[index],
                    payload={
                        "chunk_id": row.id,
                        "document_id": document.id,
                        "source_type": document.source_type,
                        "source_ref": document.source_ref,
                        "content": chunk,
                        "environment": document.metadata_json.get("environment", "*"),
                        "service": document.metadata_json.get("service", ""),
                    },
                )
            )

    if points:
        vector_store.upsert(points)

    job.status = EmbeddingJobStatus.COMPLETED
    job.finished_at = datetime.utcnow()
    document.ingestion_status = "indexed"
