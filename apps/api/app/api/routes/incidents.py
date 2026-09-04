from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import EngineerOrAdminUser, ViewerOrAboveUser
from app.db.session import get_db
from app.models.entities import EvidenceItem, Incident, IncidentComment, IncidentEvent, IncidentStatus
from app.schemas.incident import (
    EvidenceCreate,
    EvidenceResponse,
    IncidentCommentCreate,
    IncidentCommentResponse,
    IncidentCreate,
    IncidentEventResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/incidents", tags=["incidents"])


async def _get_incident_or_404(db: AsyncSession, incident_id: str) -> Incident:
    incident = (await db.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


async def _record_event(
    db: AsyncSession,
    incident_id: str,
    actor_id: str | None,
    event_type: str,
    message: str,
    metadata_json: dict | None = None,
) -> None:
    db.add(
        IncidentEvent(
            incident_id=incident_id,
            actor_id=actor_id,
            event_type=event_type,
            message=message,
            metadata_json=metadata_json or {},
        )
    )


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[IncidentResponse]:
    incidents = (
        await db.execute(select(Incident).order_by(Incident.updated_at.desc()).limit(200))
    ).scalars().all()
    return [IncidentResponse.model_validate(item) for item in incidents]


@router.post("", response_model=IncidentResponse)
async def create_incident(
    payload: IncidentCreate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        priority=payload.priority,
        environment=payload.environment,
        affected_systems=payload.affected_systems,
        tags=payload.tags,
        assignee_id=payload.assignee_id,
        team_id=payload.team_id,
    )
    db.add(incident)
    await db.flush()

    await _record_event(
        db,
        incident.id,
        current_user.id,
        "incident_created",
        f"Incident created by {current_user.email}",
    )
    await log_audit_event(db, current_user.id, "incident.create", "incident", incident.id)
    await db.commit()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    incident = await _get_incident_or_404(db, incident_id)
    return IncidentResponse.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    incident = await _get_incident_or_404(db, incident_id)

    previous_status = incident.status
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(incident, field, value)

    if payload.status in {IncidentStatus.RESOLVED, IncidentStatus.CLOSED}:
        incident.resolved_at = datetime.utcnow()

    if payload.status and payload.status != previous_status:
        await _record_event(
            db,
            incident.id,
            current_user.id,
            "incident_status_changed",
            f"Status changed from {previous_status.value} to {payload.status.value}",
        )

    await log_audit_event(
        db,
        current_user.id,
        "incident.update",
        "incident",
        incident.id,
        {"updated_fields": list(updates.keys())},
    )

    await db.commit()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}/events", response_model=list[IncidentEventResponse])
async def list_events(
    incident_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[IncidentEventResponse]:
    await _get_incident_or_404(db, incident_id)
    events = (
        await db.execute(
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.created_at.desc())
            .limit(500)
        )
    ).scalars().all()
    return [IncidentEventResponse.model_validate(item) for item in events]


@router.post("/{incident_id}/comments", response_model=IncidentCommentResponse)
async def create_comment(
    incident_id: str,
    payload: IncidentCommentCreate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> IncidentCommentResponse:
    await _get_incident_or_404(db, incident_id)

    comment = IncidentComment(
        incident_id=incident_id,
        author_id=current_user.id,
        body=payload.body,
        provenance=payload.provenance,
        citations=payload.citations,
    )
    db.add(comment)

    await _record_event(
        db,
        incident_id,
        current_user.id,
        "comment_added",
        "Comment added",
        {"provenance": payload.provenance.value},
    )
    await log_audit_event(db, current_user.id, "incident.comment.add", "incident", incident_id)

    await db.commit()
    await db.refresh(comment)
    return IncidentCommentResponse.model_validate(comment)


@router.get("/{incident_id}/comments", response_model=list[IncidentCommentResponse])
async def list_comments(
    incident_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[IncidentCommentResponse]:
    await _get_incident_or_404(db, incident_id)
    comments = (
        await db.execute(
            select(IncidentComment)
            .where(IncidentComment.incident_id == incident_id)
            .order_by(IncidentComment.created_at.desc())
            .limit(500)
        )
    ).scalars().all()
    return [IncidentCommentResponse.model_validate(item) for item in comments]


@router.post("/{incident_id}/evidence", response_model=EvidenceResponse)
async def create_evidence(
    incident_id: str,
    payload: EvidenceCreate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    await _get_incident_or_404(db, incident_id)

    evidence = EvidenceItem(
        incident_id=incident_id,
        author_id=current_user.id,
        title=payload.title,
        evidence_type=payload.evidence_type,
        content=payload.content,
        source_url=payload.source_url,
        provenance=payload.provenance,
        metadata_json=payload.metadata_json,
    )
    db.add(evidence)

    await _record_event(
        db,
        incident_id,
        current_user.id,
        "evidence_added",
        f"Evidence added: {payload.title}",
    )
    await log_audit_event(db, current_user.id, "incident.evidence.add", "incident", incident_id)

    await db.commit()
    await db.refresh(evidence)
    return EvidenceResponse.model_validate(evidence)


@router.post("/{incident_id}/evidence/upload", response_model=EvidenceResponse)
async def upload_evidence_file(
    incident_id: str,
    title: str,
    current_user: EngineerOrAdminUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    from app.core.config import get_settings

    await _get_incident_or_404(db, incident_id)
    settings = get_settings()

    allowed_types = {
        "text/plain",
        "application/json",
        "image/png",
        "image/jpeg",
        "application/pdf",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(data) > max_size:
        raise HTTPException(status_code=400, detail="File exceeds maximum size")

    upload_root = Path(settings.file_storage_path)
    upload_root.mkdir(parents=True, exist_ok=True)
    safe_name = f"{incident_id}_{datetime.utcnow().timestamp()}_{file.filename}".replace(" ", "_")
    file_path = upload_root / safe_name
    file_path.write_bytes(data)

    evidence = EvidenceItem(
        incident_id=incident_id,
        author_id=current_user.id,
        title=title,
        evidence_type="file",
        content="",
        source_url="",
        file_path=str(file_path),
        metadata_json={"filename": file.filename, "content_type": file.content_type, "size": len(data)},
    )
    db.add(evidence)

    await _record_event(
        db,
        incident_id,
        current_user.id,
        "evidence_uploaded",
        f"File evidence uploaded: {file.filename}",
    )

    await log_audit_event(db, current_user.id, "incident.evidence.upload", "incident", incident_id)

    await db.commit()
    await db.refresh(evidence)
    return EvidenceResponse.model_validate(evidence)


@router.get("/{incident_id}/evidence", response_model=list[EvidenceResponse])
async def list_evidence(
    incident_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[EvidenceResponse]:
    await _get_incident_or_404(db, incident_id)
    evidence = (
        await db.execute(
            select(EvidenceItem)
            .where(EvidenceItem.incident_id == incident_id)
            .order_by(EvidenceItem.created_at.desc())
            .limit(500)
        )
    ).scalars().all()
    return [EvidenceResponse.model_validate(item) for item in evidence]
