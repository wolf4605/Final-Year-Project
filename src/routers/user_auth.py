<<<<<<< HEAD
"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 11:19:18

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 13:41:14

* License: MIT
* Copyright© BondVault PK. All rights reserved.
""""""User login and authenticated profile endpoints."""
=======
"""User login and authenticated profile endpoints."""
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a

import logging
from typing import Annotated

<<<<<<< HEAD
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException

from ..database import DB
from ..models.user_model import UserInfo
from ..responses import UserLoginResponse
from ..utilities.auth import verify_password
=======
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database.wrapper import DB
from ..models.auth_model import UserLoginResponse
from ..models.user_model import UserInfo
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a
from ..utilities.auth_dependencies import get_current_user
from ..utilities.auth_tokens import create_access_token, token_lifetime

logger = logging.getLogger("application.audit")
router = APIRouter(prefix="/users", tags=["User Authentication"])


@router.post(
    "/auth/login",
    response_model=UserLoginResponse,
    summary="Log in as a user",
)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> UserLoginResponse:
    """Authenticate a user with an OAuth2 username/email and password form."""
<<<<<<< HEAD
    record = await DB.fetchrow(
        """
        SELECT "id", "username", "email", "password_hash", "first_name",
               "last_name", "contact", "created_at", "is_verified",
               "verified_by", "last_login"
        FROM "users"
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
=======
    user = await DB.User.authenticate(
        credentials.username,
        credentials.password,
    )
    if user is None:
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a
        logger.warning(
            "user authentication failed",
            extra={"event": "auth.login.failed", "role": "user"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

<<<<<<< HEAD
    user = UserInfo.model_validate(dict(record))
    if await DB.fetchval(
        """
        UPDATE "users"
        SET "last_login" = CURRENT_TIMESTAMP
        WHERE "id" = $1
        RETURNING TRUE
        """,
        user.id,
    ) is not True:
=======
    if not await DB.User.record_login(user.id):
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, "user")
    logger.info(
        "user authenticated",
        extra={
            "event": "auth.login.success",
            "role": "user",
            "subject_id": str(user.id),
        },
    )
    return UserLoginResponse(
        access_token=token,
        expires_in=int(token_lifetime().total_seconds()),
        payload=user,
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get the authenticated user's profile",
)
async def get_user_info(
<<<<<<< HEAD
    user_info: Annotated[UserInfo, Depends(get_current_user)],
) -> UserInfo:
    """Return the authenticated user's profile without a separate user ID."""
    return user_info
=======
    payload: Annotated[UserInfo, Depends(get_current_user)],
) -> UserInfo:
    """Return the authenticated user's profile without a separate user ID."""
    return payload
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a


__all__ = ["router"]
