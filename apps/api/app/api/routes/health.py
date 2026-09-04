from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.rag.vector_store import VectorStore

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()
    await db.execute(text("SELECT 1"))

    vector_ok = True
    try:
        store = VectorStore()
        store.ensure_collection()
    except Exception:
        vector_ok = False

    return {
        "status": "ready" if vector_ok else "degraded",
        "dependencies": {"database": "ok", "qdrant": "ok" if vector_ok else "error"},
        "environment": settings.app_env,
    }
