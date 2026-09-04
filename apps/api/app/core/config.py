from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "OpsCentreDan"
    log_level: str = "INFO"
    demo_mode: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:3000"

    jwt_secret: str = Field(..., min_length=16)
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_minutes: int = 10080
    jwt_issuer: str = "opscentredan-api"
    jwt_audience: str = "opscentredan-web"

    auth_max_failed_attempts: int = 5
    auth_failure_window_minutes: int = 15
    auth_lockout_minutes: int = 15

    database_url: str

    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "knowledge_chunks"

    file_storage_path: str = "/data/uploads"
    max_upload_size_mb: int = 10

    admin_email: str = "admin@opscentredan.dev"
    admin_password: str = "ChangeMeNow123!"

    llm_provider: str = "openai_compatible"
    embedding_provider: str = "openai_compatible"
    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-large"


@lru_cache
def get_settings() -> Settings:
    return Settings()
