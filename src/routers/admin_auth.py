"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 11:19:18

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 13:41:38

* License: MIT
* Copyright© BondVault PK. All rights reserved.
""""""Administrator login and authenticated profile endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException

from ..database import DB
from ..models.admin_model import AdminInfo
from ..responses import AdminLoginResponse
from ..utilities.auth import verify_password
from ..utilities.auth_dependencies import get_current_admin
from ..utilities.auth_tokens import create_access_token, token_lifetime

logger = logging.getLogger("application.audit")
router = APIRouter(prefix="/admins",
                   tags=["Admin Authentication"])


@router.post(
    "/auth/login",
    response_model=AdminLoginResponse,
    summary="Log in as an administrator",
)
async def login_admin(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AdminLoginResponse:
    """Authenticate an administrator with username/email and password form data."""
    record = await DB.fetchrow(
        """
        SELECT "id", "username", "email", "password_hash", "first_name",
               "last_name", "contact", "created_at", "is_superuser"
        FROM "admins"
        WHERE "username" = $1 OR LOWER("email") = LOWER($1)
        ORDER BY ("username" = $1) DESC
        LIMIT 1
        """,
        credentials.username,
    )
    if record is None or not verify_password(
        credentials.password,
        record["password_hash"],
    ):
        logger.warning(
            "administrator authentication failed",
            extra={"event": "auth.login.failed", "role": "admin"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = AdminInfo.model_validate(dict(record))
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
    admin_info: Annotated[AdminInfo, Depends(get_current_admin)],
) -> AdminInfo:
    """Return the authenticated administrator's profile without a separate ID."""
    return admin_info


__all__ = ["router"]
