from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ViewerOrAboveUser
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    oauth2_scheme,
    verify_password,
)
from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.services.audit import log_audit_event
from app.services.auth_store import (
    clear_failed_logins,
    is_token_jti_revoked,
    normalize_email,
    register_failed_login,
    revoke_token_jti,
    seconds_until_unlock,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _invalid_credentials_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    settings = get_settings()
    email = normalize_email(str(payload.email))

    lock_seconds = await seconds_until_unlock(email)
    if lock_seconds > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later.",
        )

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    password_hash = user.hashed_password if user else DUMMY_PASSWORD_HASH
    password_valid = verify_password(payload.password, password_hash)

    if not user or not user.is_active or not password_valid:
        attempts, lockout = await register_failed_login(email)
        await log_audit_event(
            db,
            user.id if user else None,
            "auth.login.failed",
            "user",
            user.id if user else "unknown",
            {
                "email": email,
                "attempts": attempts,
                "lockout_seconds": lockout,
                "ip": request.client.host if request.client else "unknown",
            },
        )
        await db.commit()
        raise _invalid_credentials_error()

    await clear_failed_logins(email)

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    await log_audit_event(
        db,
        user.id,
        "auth.login.success",
        "user",
        user.id,
        {"ip": request.client.host if request.client else "unknown"},
    )
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_seconds=settings.jwt_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_tokens(
    request: Request,
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    settings = get_settings()
    claims = decode_token(payload.refresh_token, TokenType.REFRESH)

    jti = str(claims.get("jti", ""))
    sub = str(claims.get("sub", ""))
    exp = int(claims.get("exp", 0))

    if not jti or not sub or not exp:
        raise _invalid_credentials_error()

    if await is_token_jti_revoked(jti):
        raise _invalid_credentials_error()

    user = (await db.execute(select(User).where(User.id == sub))).scalar_one_or_none()
    if not user or not user.is_active:
        raise _invalid_credentials_error()

    if not await revoke_token_jti(jti, exp):
        raise HTTPException(status_code=503, detail="Refresh service unavailable")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    await log_audit_event(
        db,
        user.id,
        "auth.refresh.success",
        "user",
        user.id,
        {"ip": request.client.host if request.client else "unknown"},
    )
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_seconds=settings.jwt_expire_minutes * 60,
    )


@router.post("/logout")
@limiter.limit("60/minute")
async def logout(
    request: Request,
    payload: LogoutRequest,
    current_user: ViewerOrAboveUser,
    access_token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_claims = decode_token(access_token, TokenType.ACCESS)
    access_jti = str(access_claims.get("jti", ""))
    access_exp = int(access_claims.get("exp", 0))

    if access_jti and access_exp:
        if not await revoke_token_jti(access_jti, access_exp):
            raise HTTPException(status_code=503, detail="Logout service unavailable")

    if payload.refresh_token:
        refresh_claims = decode_token(payload.refresh_token, TokenType.REFRESH)
        refresh_sub = str(refresh_claims.get("sub", ""))
        refresh_jti = str(refresh_claims.get("jti", ""))
        refresh_exp = int(refresh_claims.get("exp", 0))

        if refresh_sub != current_user.id:
            raise HTTPException(status_code=403, detail="Refresh token does not belong to current user")

        if refresh_jti and refresh_exp:
            if not await revoke_token_jti(refresh_jti, refresh_exp):
                raise HTTPException(status_code=503, detail="Logout service unavailable")

    await log_audit_event(
        db,
        current_user.id,
        "auth.logout.success",
        "user",
        current_user.id,
        {"ip": request.client.host if request.client else "unknown"},
    )
    await db.commit()

    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: ViewerOrAboveUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
