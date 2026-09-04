from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import ConnectorType, ProviderType


class ConnectorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    connector_type: ConnectorType
    shared_secret: str = ""
    config_json: dict = Field(default_factory=dict)


class ConnectorResponse(BaseModel):
    id: str
    name: str
    connector_type: ConnectorType
    is_active: bool
    config_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderConfigCreate(BaseModel):
    provider_type: ProviderType
    name: str = Field(min_length=2, max_length=120)
    is_active: bool = True
    config_json: dict = Field(default_factory=dict)


class ProviderConfigResponse(BaseModel):
    id: str
    provider_type: ProviderType
    name: str
    is_active: bool
    config_json: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
