from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import (
    assistant,
    auth,
    health,
    incidents,
    integrations,
    knowledge,
    onboarding,
    reports,
    webhooks,
)
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.rag.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    Path(settings.file_storage_path).mkdir(parents=True, exist_ok=True)

    try:
        store = VectorStore()
        store.ensure_collection()
    except Exception:
        # Keep API booting; readiness endpoint signals degradation.
        pass

    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.api_cors_origins.split(",") if item.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(incidents.router, prefix=api_prefix)
app.include_router(integrations.router, prefix=api_prefix)
app.include_router(webhooks.router, prefix=api_prefix)
app.include_router(knowledge.router, prefix=api_prefix)
app.include_router(assistant.router, prefix=api_prefix)
app.include_router(onboarding.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)


@app.get("/")
async def root() -> dict:
    return {"name": settings.app_name, "status": "ok"}
