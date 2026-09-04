from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AuditEvent


async def log_audit_event(
    db: AsyncSession,
    actor_id: str | None,
    event_type: str,
    target_type: str,
    target_id: str,
    metadata_json: dict | None = None,
) -> None:
    event = AuditEvent(
        actor_id=actor_id,
        event_type=event_type,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata_json or {},
    )
    db.add(event)
