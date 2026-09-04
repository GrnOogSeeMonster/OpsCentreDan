import asyncio

from celery import shared_task
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import EmbeddingJob, EmbeddingJobStatus, KnowledgeDocument
from app.services.knowledge_ingestion import process_embedding_job


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def process_embedding_job_task(self, job_id: str) -> str:
    async def _runner() -> None:
        async with SessionLocal() as db:
            try:
                await process_embedding_job(db, job_id)
                await db.commit()
            except Exception as exc:
                await db.rollback()
                job = (
                    await db.execute(select(EmbeddingJob).where(EmbeddingJob.id == job_id))
                ).scalar_one_or_none()
                if job:
                    job.status = EmbeddingJobStatus.FAILED
                    job.error_message = str(exc)[:2000]
                    doc = (
                        await db.execute(
                            select(KnowledgeDocument).where(KnowledgeDocument.id == job.document_id)
                        )
                    ).scalar_one_or_none()
                    if doc:
                        doc.ingestion_status = "failed"
                    await db.commit()
                raise

    asyncio.run(_runner())
    return f"processed:{job_id}"
