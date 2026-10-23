"""Administrator login and authenticated profile endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database.wrapper import DB
from ..models.admin_model import AdminInfo
from ..models.auth_model import AdminLoginResponse
from ..utilities.auth_dependencies import get_current_admin
from ..utilities.auth_tokens import create_access_token, token_lifetime

logger = logging.getLogger("application.audit")
router = APIRouter(prefix="/admins", tags=["Admin Authentication"])


@router.post(
    "/auth/login",
    response_model=AdminLoginResponse,
    summary="Log in as an administrator",
)
async def login_admin(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AdminLoginResponse:
    """Authenticate an administrator with username/email and password form data."""
    admin = await DB.Admin.authenticate(
        credentials.username,
        credentials.password,
    )
    if admin is None:
        logger.warning(
            "administrator authentication failed",
            extra={"event": "auth.login.failed", "role": "admin"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(admin.id, "admin")
    logger.info(
        "administrator authenticated",
        extra={
            "event": "auth.login.success",
            "role": "admin",
            "subject_id": str(admin.id),
        },
    )
    return AdminLoginResponse(
        access_token=token,
        expires_in=int(token_lifetime().total_seconds()),
        payload=admin,
    )


@router.get(
    "/me",
    response_model=AdminInfo,
    summary="Get the authenticated administrator's profile",
)
async def get_admin_info(
    payload: Annotated[AdminInfo, Depends(get_current_admin)],
) -> AdminInfo:
    """Return the authenticated administrator's profile without a separate ID."""
    return payload


__all__ = ["router"]
