import os

import pytest
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.security import TokenType, create_access_token, create_refresh_token, decode_token
from app.services.auth_store import normalize_email


def _configure_test_env() -> None:
    os.environ["JWT_SECRET"] = "unit-test-secret-1234567890"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/test"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
    os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
    os.environ["JWT_ISSUER"] = "opscentredan-api"
    os.environ["JWT_AUDIENCE"] = "opscentredan-web"
    get_settings.cache_clear()


def test_create_and_decode_access_token() -> None:
    _configure_test_env()
    token = create_access_token("user-123")
    claims = decode_token(token, TokenType.ACCESS)

    assert claims["sub"] == "user-123"
    assert claims["type"] == "access"
    assert claims["jti"]


def test_refresh_token_rejected_as_access() -> None:
    _configure_test_env()
    token = create_refresh_token("user-123")

    with pytest.raises(HTTPException):
        decode_token(token, TokenType.ACCESS)


def test_normalize_email_lowercases_and_trims() -> None:
    assert normalize_email("  Admin@OpsCentreDan.Dev ") == "admin@opscentredan.dev"
