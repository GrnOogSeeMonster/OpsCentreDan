from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.rate_limit import limiter
from app.db.session import get_db
from app.integrations.webhooks.adapters import normalize_alert
from app.models.entities import AlertEvent, Incident, IncidentEvent, IntegrationConnector
from app.services.audit import log_audit_event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/{connector_id}")
@limiter.limit("60/minute")
async def ingest_alert(
    connector_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_connector_secret: str | None = Header(default=None),
) -> dict:
    connector = (
        await db.execute(select(IntegrationConnector).where(IntegrationConnector.id == connector_id))
    ).scalar_one_or_none()
    if not connector or not connector.is_active:
        raise HTTPException(status_code=404, detail="Connector not found")

    if connector.shared_secret and connector.shared_secret != (x_connector_secret or ""):
        raise HTTPException(status_code=403, detail="Invalid connector secret")

    payload = await request.json()
    normalized = normalize_alert(connector.connector_type, payload)

    incident = Incident(
        title=normalized.title,
        description=normalized.description,
        severity=normalized.severity,
        environment=normalized.environment,
        tags=normalized.tags,
        affected_systems=[normalized.service],
        priority=2 if normalized.severity.value in {"sev1", "sev2"} else 3,
    )
    db.add(incident)
    await db.flush()

    alert_event = AlertEvent(
        incident_id=incident.id,
        connector_id=connector.id,
        provider=connector.connector_type,
        external_alert_id=normalized.external_alert_id,
        title=normalized.title,
        severity=normalized.severity.value,
        environment=normalized.environment,
        service=normalized.service,
        normalized_payload={
            "title": normalized.title,
            "description": normalized.description,
            "severity": normalized.severity.value,
            "environment": normalized.environment,
            "service": normalized.service,
            "tags": normalized.tags,
        },
        raw_payload=normalized.raw_payload,
    )
    db.add(alert_event)

    db.add(
        IncidentEvent(
            incident_id=incident.id,
            actor_id=None,
            event_type="alert_ingested",
            message=f"Alert received from {connector.connector_type.value}",
            metadata_json={"connector_id": connector.id, "external_alert_id": normalized.external_alert_id},
        )
    )

    await log_audit_event(
        db,
        None,
        "alert.ingested",
        "incident",
        incident.id,
        {"connector_id": connector.id, "provider": connector.connector_type.value},
    )

    await db.commit()
    await db.refresh(incident)

    return {"incident_id": incident.id, "status": incident.status.value}
