"""FastAPI dependencies for authenticated users and administrators."""

from typing import Annotated, Literal
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from ..database.wrapper import DB
from ..models.auth_model import TokenClaims
from ..models.admin_model import AdminInfo
from ..models.user_model import UserInfo
from .auth_tokens import (
    ACCESS_TOKEN_EXPIRES_HEADER,
    ACCESS_TOKEN_HEADER,
    create_access_token,
    decode_access_token,
    token_lifetime,
)

user_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/auth/login",
    scheme_name="UserOAuth2",
    description="Sign in with a user account username or email address and password.",
    auto_error=False,
)
admin_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/admins/auth/login",
    scheme_name="AdminOAuth2",
    description="Sign in with an administrator username or email address and password.",
    auto_error=False,
)


def _unauthorized() -> HTTPException:
    """Create a consistent bearer-authentication failure."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid bearer access token is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _token_claims(
    token: str | None,
) -> TokenClaims:
    """Decode OAuth2 bearer credentials, translating invalid tokens to 401."""
    if token is None:
        raise _unauthorized()
    try:
        return decode_access_token(token)
    except (jwt.InvalidTokenError, ValidationError) as error:
        raise _unauthorized() from error


def _refresh_response(
    response: Response,
    subject: UUID,
    role: Literal["user", "admin"],
) -> None:
    """Attach a freshly expiring token to each authenticated response."""
    response.headers[ACCESS_TOKEN_HEADER] = create_access_token(subject, role)
    response.headers[ACCESS_TOKEN_EXPIRES_HEADER] = str(
        int(token_lifetime().total_seconds())
    )


async def get_current_user(
    credentials: Annotated[
        str | None,
        Depends(user_oauth2_scheme),
    ],
    response: Response,
) -> UserInfo:
    """Resolve and refresh the authenticated user's payload."""
    claims = _token_claims(credentials)
    if claims.role != "user":
        raise _unauthorized()

    payload = await DB.User.get_by_id(claims.sub)
    if payload is None:
        raise _unauthorized()

    _refresh_response(response, payload.id, "user")
    return payload


async def get_current_admin(
    credentials: Annotated[
        str | None,
        Depends(admin_oauth2_scheme),
    ],
    response: Response,
    request: Request,
) -> AdminInfo:
    """Resolve and refresh the authenticated administrator payload."""
    claims = _token_claims(credentials)
    if claims.role != "admin":
        raise _unauthorized()

    payload = await DB.Admin.get_by_id(claims.sub)
    if payload is None:
        raise _unauthorized()

    request.state.admin_payload = payload
    _refresh_response(response, payload.id, "admin")
    return payload


__all__ = ["get_current_admin", "get_current_user"]
