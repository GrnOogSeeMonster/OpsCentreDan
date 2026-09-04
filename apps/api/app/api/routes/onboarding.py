from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, ViewerOrAboveUser
from app.db.session import get_db
from app.models.entities import IntegrationConnector, ProviderConfiguration, ProviderType
from app.schemas.onboarding import OnboardingStatusResponse, OnboardingStepUpdate

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


STEP_TO_PROVIDER: dict[str, ProviderType] = {
    "cloud_provider": ProviderType.AWS,
    "observability_provider": ProviderType.OBSERVABILITY,
    "ai_provider": ProviderType.AI,
    "embedding_provider": ProviderType.EMBEDDING,
    "oidc": ProviderType.OIDC,
}


@router.get("/status", response_model=OnboardingStatusResponse)
async def onboarding_status(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> OnboardingStatusResponse:
    completed_steps: list[str] = ["auth_setup"]

    provider_rows = (await db.execute(select(ProviderConfiguration))).scalars().all()
    connectors = (await db.execute(select(IntegrationConnector))).scalars().all()

    if provider_rows:
        completed_steps.append("provider_configs")
    if connectors:
        completed_steps.append("connector_setup")

    checks = [
        {"name": "provider_configs", "ok": len(provider_rows) > 0},
        {"name": "connectors", "ok": len(connectors) > 0},
        {"name": "first_incident_test", "ok": False},
    ]

    return OnboardingStatusResponse(completed_steps=completed_steps, checks=checks)


@router.post("/step", response_model=OnboardingStatusResponse)
async def update_step(
    payload: OnboardingStepUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> OnboardingStatusResponse:
    provider_type = STEP_TO_PROVIDER.get(payload.step)
    if provider_type:
        cfg = ProviderConfiguration(
            provider_type=provider_type,
            name=payload.step,
            is_active=True,
            config_json=payload.payload,
        )
        db.add(cfg)
        await db.commit()

    return await onboarding_status(current_user, db)
