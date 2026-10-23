"""User login and authenticated profile endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database.wrapper import DB
from ..models.auth_model import UserLoginResponse
from ..models.user_model import UserInfo
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
    user = await DB.User.authenticate(
        credentials.username,
        credentials.password,
    )
    if user is None:
        logger.warning(
            "user authentication failed",
            extra={"event": "auth.login.failed", "role": "user"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not await DB.User.record_login(user.id):
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
    payload: Annotated[UserInfo, Depends(get_current_user)],
) -> UserInfo:
    """Return the authenticated user's profile without a separate user ID."""
    return payload


__all__ = ["router"]
