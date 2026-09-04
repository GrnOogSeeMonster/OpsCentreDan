from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import COEStatus


class COEGenerateRequest(BaseModel):
    label: str = Field(default="COE", min_length=2, max_length=80)


class COEUpdateRequest(BaseModel):
    summary: str | None = None
    timeline: list[dict] | None = None
    findings: list[dict] | None = None
    impact_analysis: str | None = None
    root_cause: str | None = None
    remediation: str | None = None
    preventative_recommendations: str | None = None


class COEReportResponse(BaseModel):
    id: str
    incident_id: str
    label: str
    status: COEStatus
    summary: str
    timeline: list[dict]
    findings: list[dict]
    impact_analysis: str
    root_cause: str
    remediation: str
    preventative_recommendations: str
    finalized_at: datetime | None
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str
    owner_id: str | None = None
    due_date: datetime | None = None


class ActionItemResponse(BaseModel):
    id: str
    report_id: str
    description: str
    owner_id: str | None
    due_date: datetime | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
