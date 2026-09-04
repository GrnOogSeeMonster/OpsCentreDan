from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import EngineerOrAdminUser, ViewerOrAboveUser
from app.db.session import get_db
from app.models.entities import ActionItem, COEReport, COEStatus, EvidenceItem, Incident, IncidentEvent
from app.schemas.report import (
    ActionItemCreate,
    ActionItemResponse,
    COEGenerateRequest,
    COEReportResponse,
    COEUpdateRequest,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/reports", tags=["reports"])


async def _get_or_404_report(db: AsyncSession, report_id: str) -> COEReport:
    report = (await db.execute(select(COEReport).where(COEReport.id == report_id))).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/incidents/{incident_id}/generate", response_model=COEReportResponse)
async def generate_report(
    incident_id: str,
    payload: COEGenerateRequest,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> COEReportResponse:
    incident = (await db.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    events = (
        await db.execute(
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.created_at.asc())
        )
    ).scalars().all()
    evidence = (
        await db.execute(
            select(EvidenceItem)
            .where(EvidenceItem.incident_id == incident_id)
            .order_by(EvidenceItem.created_at.asc())
        )
    ).scalars().all()

    existing = (
        await db.execute(select(COEReport).where(COEReport.incident_id == incident_id))
    ).scalar_one_or_none()
    if existing:
        report = existing
    else:
        report = COEReport(incident_id=incident_id)
        db.add(report)

    report.label = payload.label
    report.summary = (
        f"{incident.title} ({incident.severity.value}) in {incident.environment} moved through "
        f"{incident.status.value} state with {len(events)} recorded events."
    )
    report.timeline = [
        {
            "timestamp": item.created_at.isoformat(),
            "event_type": item.event_type,
            "message": item.message,
        }
        for item in events
    ]
    report.findings = [
        {
            "title": ev.title,
            "type": ev.evidence_type,
            "provenance": ev.provenance.value,
            "source_url": ev.source_url,
        }
        for ev in evidence
    ]
    report.impact_analysis = (
        "Impact requires operator verification. Draft generated from timeline and evidence."
    )
    report.root_cause = "Draft hypothesis pending human confirmation."
    report.remediation = incident.resolution_summary or "Mitigation and remediation notes to be completed."
    report.preventative_recommendations = "Add targeted monitors, runbook updates, and regression guards."
    report.status = COEStatus.DRAFT

    await log_audit_event(db, current_user.id, "coe.generate", "incident", incident_id)
    await db.commit()
    await db.refresh(report)

    return COEReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=COEReportResponse)
async def get_report(
    report_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> COEReportResponse:
    report = await _get_or_404_report(db, report_id)
    return COEReportResponse.model_validate(report)


@router.patch("/{report_id}", response_model=COEReportResponse)
async def update_report(
    report_id: str,
    payload: COEUpdateRequest,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> COEReportResponse:
    report = await _get_or_404_report(db, report_id)

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(report, key, value)

    await log_audit_event(db, current_user.id, "coe.update", "coe_report", report.id)
    await db.commit()
    await db.refresh(report)
    return COEReportResponse.model_validate(report)


@router.post("/{report_id}/finalize", response_model=COEReportResponse)
async def finalize_report(
    report_id: str,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> COEReportResponse:
    report = await _get_or_404_report(db, report_id)
    report.status = COEStatus.FINALIZED
    report.finalized_at = datetime.utcnow()
    await log_audit_event(db, current_user.id, "coe.finalize", "coe_report", report.id)
    await db.commit()
    await db.refresh(report)
    return COEReportResponse.model_validate(report)


@router.post("/{report_id}/actions", response_model=ActionItemResponse)
async def create_action_item(
    report_id: str,
    payload: ActionItemCreate,
    current_user: EngineerOrAdminUser,
    db: AsyncSession = Depends(get_db),
) -> ActionItemResponse:
    await _get_or_404_report(db, report_id)
    item = ActionItem(
        report_id=report_id,
        description=payload.description,
        owner_id=payload.owner_id,
        due_date=payload.due_date,
    )
    db.add(item)
    await log_audit_event(db, current_user.id, "coe.action_item.create", "coe_report", report_id)
    await db.commit()
    await db.refresh(item)
    return ActionItemResponse.model_validate(item)


@router.get("/{report_id}/actions", response_model=list[ActionItemResponse])
async def list_action_items(
    report_id: str,
    current_user: ViewerOrAboveUser,
    db: AsyncSession = Depends(get_db),
) -> list[ActionItemResponse]:
    await _get_or_404_report(db, report_id)
    rows = (
        await db.execute(
            select(ActionItem).where(ActionItem.report_id == report_id).order_by(ActionItem.created_at.asc())
        )
    ).scalars().all()
    return [ActionItemResponse.model_validate(item) for item in rows]
