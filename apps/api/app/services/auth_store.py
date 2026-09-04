from __future__ import annotations

from functools import lru_cache
from time import time

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def normalize_email(value: str) -> str:
    return value.strip().lower()


def _failed_count_key(email: str) -> str:
    return f"auth:failed:{email}"


def _lock_key(email: str) -> str:
    return f"auth:lock:{email}"


def _revoked_key(jti: str) -> str:
    return f"auth:revoked:{jti}"


async def seconds_until_unlock(email: str) -> int:
    redis = get_redis_client()
    try:
        ttl = await redis.ttl(_lock_key(email))
    except RedisError:
        return 0
    return ttl if ttl and ttl > 0 else 0


async def register_failed_login(email: str) -> tuple[int, int]:
    """Returns (attempt_count, lockout_seconds)."""
    settings = get_settings()
    redis = get_redis_client()
    count_key = _failed_count_key(email)

    try:
        attempts = await redis.incr(count_key)
        if attempts == 1:
            await redis.expire(count_key, settings.auth_failure_window_minutes * 60)

        if attempts >= settings.auth_max_failed_attempts:
            lock_seconds = settings.auth_lockout_minutes * 60
            await redis.set(_lock_key(email), "1", ex=lock_seconds)
            return attempts, lock_seconds
    except RedisError:
        return 0, 0

    return attempts, 0


async def clear_failed_logins(email: str) -> None:
    redis = get_redis_client()
    try:
        await redis.delete(_failed_count_key(email), _lock_key(email))
    except RedisError:
        return


async def revoke_token_jti(jti: str, exp_unix: int) -> bool:
    """Returns True if revoke marker is persisted, False if backend unavailable."""
    redis = get_redis_client()
    ttl = int(exp_unix - time())
    if ttl <= 0:
        return True

    try:
        await redis.set(_revoked_key(jti), "1", ex=ttl)
        return True
    except RedisError:
        return False


async def is_token_jti_revoked(jti: str) -> bool:
    redis = get_redis_client()
    try:
        return await redis.exists(_revoked_key(jti)) == 1
    except RedisError:
        return False
