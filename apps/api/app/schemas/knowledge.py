from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import EmbeddingJobStatus


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    source_type: str = Field(default="text")
    source_ref: str = ""
    text_content: str = ""
    metadata_json: dict = Field(default_factory=dict)


class KnowledgeDocumentResponse(BaseModel):
    id: str
    title: str
    source_type: str
    source_ref: str
    ingestion_status: str
    metadata_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class EmbeddingJobResponse(BaseModel):
    id: str
    document_id: str
    status: EmbeddingJobStatus
    attempts: int
    error_message: str
    created_at: datetime

    class Config:
        from_attributes = True
