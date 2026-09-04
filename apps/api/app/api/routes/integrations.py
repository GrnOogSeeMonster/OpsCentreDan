from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, ViewerOrAboveUser
from app.db.session import get_db
from app.models.entities import IntegrationConnector, ProviderConfiguration
from app.schemas.integration import (
    ConnectorCreate,
    ConnectorResponse,
    ProviderConfigCreate,
    ProviderConfigResponse,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/connectors", response_model=list[ConnectorResponse])
async def list_connectors(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[ConnectorResponse]:
    connectors = (
        await db.execute(select(IntegrationConnector).order_by(IntegrationConnector.created_at.desc()))
    ).scalars().all()
    return [ConnectorResponse.model_validate(item) for item in connectors]


@router.post("/connectors", response_model=ConnectorResponse)
async def create_connector(
    payload: ConnectorCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> ConnectorResponse:
    connector = IntegrationConnector(
        name=payload.name,
        connector_type=payload.connector_type,
        shared_secret=payload.shared_secret,
        config_json=payload.config_json,
    )
    db.add(connector)
    await db.flush()
    await log_audit_event(db, current_user.id, "connector.create", "connector", connector.id)
    await db.commit()
    await db.refresh(connector)
    return ConnectorResponse.model_validate(connector)


@router.get("/providers", response_model=list[ProviderConfigResponse])
async def list_provider_configs(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[ProviderConfigResponse]:
    rows = (
        await db.execute(
            select(ProviderConfiguration).order_by(ProviderConfiguration.created_at.desc())
        )
    ).scalars().all()
    return [ProviderConfigResponse.model_validate(item) for item in rows]


@router.post("/providers", response_model=ProviderConfigResponse)
async def create_provider_config(
    payload: ProviderConfigCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> ProviderConfigResponse:
    cfg = ProviderConfiguration(
        provider_type=payload.provider_type,
        name=payload.name,
        is_active=payload.is_active,
        config_json=payload.config_json,
    )
    db.add(cfg)
    await db.flush()
    await log_audit_event(db, current_user.id, "provider_config.create", "provider_config", cfg.id)
    await db.commit()
    await db.refresh(cfg)
    return ProviderConfigResponse.model_validate(cfg)
