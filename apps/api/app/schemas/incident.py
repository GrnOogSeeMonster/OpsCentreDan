from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import IncidentStatus, ProvenanceEnum, SeverityEnum


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=400)
    description: str = ""
    severity: SeverityEnum = SeverityEnum.SEV3
    priority: int = Field(default=3, ge=1, le=5)
    environment: str = "production"
    affected_systems: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    assignee_id: str | None = None
    team_id: str | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: SeverityEnum | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: IncidentStatus | None = None
    environment: str | None = None
    affected_systems: list[str] | None = None
    tags: list[str] | None = None
    assignee_id: str | None = None
    team_id: str | None = None
    resolution_summary: str | None = None


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    status: IncidentStatus
    severity: SeverityEnum
    priority: int
    environment: str
    affected_systems: list[str]
    tags: list[str]
    assignee_id: str | None
    team_id: str | None
    resolution_summary: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IncidentEventResponse(BaseModel):
    id: str
    incident_id: str
    actor_id: str | None
    event_type: str
    message: str
    metadata_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentCommentCreate(BaseModel):
    body: str = Field(min_length=1)
    provenance: ProvenanceEnum = ProvenanceEnum.HUMAN
    citations: list[dict] = Field(default_factory=list)


class IncidentCommentResponse(BaseModel):
    id: str
    incident_id: str
    author_id: str | None
    body: str
    provenance: ProvenanceEnum
    citations: list[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class EvidenceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    evidence_type: str = "note"
    content: str = ""
    source_url: str = ""
    provenance: ProvenanceEnum = ProvenanceEnum.HUMAN
    metadata_json: dict = Field(default_factory=dict)


class EvidenceResponse(BaseModel):
    id: str
    incident_id: str
    author_id: str | None
    title: str
    evidence_type: str
    content: str
    source_url: str
    file_path: str
    provenance: ProvenanceEnum
    metadata_json: dict
    created_at: datetime

    class Config:
        from_attributes = True
