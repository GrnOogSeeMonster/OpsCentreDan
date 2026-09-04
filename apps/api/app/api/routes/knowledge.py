from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import EngineerOrAdminUser, ViewerOrAboveUser
from app.db.session import get_db
from app.models.entities import EmbeddingJob, KnowledgeDocument
from app.schemas.knowledge import (
    EmbeddingJobResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
)
from app.services.audit import log_audit_event
from app.services.knowledge_ingestion import enqueue_embedding_job
from app.tasks.jobs import process_embedding_job_task

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/documents", response_model=KnowledgeDocumentResponse)
async def create_knowledge_document(
    payload: KnowledgeDocumentCreate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentResponse:
    doc = KnowledgeDocument(
        title=payload.title,
        source_type=payload.source_type,
        source_ref=payload.source_ref,
        text_content=payload.text_content,
        metadata_json=payload.metadata_json,
        ingestion_status="queued",
        created_by_id=current_user.id,
    )
    db.add(doc)
    await db.flush()

    job = await enqueue_embedding_job(db, doc.id)
    await log_audit_event(db, current_user.id, "knowledge.document.create", "knowledge_document", doc.id)

    await db.commit()
    process_embedding_job_task.delay(job.id)

    await db.refresh(doc)
    return KnowledgeDocumentResponse.model_validate(doc)


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_documents(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeDocumentResponse]:
    docs = (
        await db.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).limit(200))
    ).scalars().all()
    return [KnowledgeDocumentResponse.model_validate(d) for d in docs]


@router.get("/jobs", response_model=list[EmbeddingJobResponse])
async def list_jobs(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[EmbeddingJobResponse]:
    jobs = (
        await db.execute(select(EmbeddingJob).order_by(EmbeddingJob.created_at.desc()).limit(200))
    ).scalars().all()
    return [EmbeddingJobResponse.model_validate(j) for j in jobs]
