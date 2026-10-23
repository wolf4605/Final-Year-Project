"""Request and response models for user and administrator authentication."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, SecretStr

from .admin_model import AdminInfo
from .user_model import UserInfo


class LoginPayload(BaseModel):
    """Credentials submitted to either login endpoint."""

    username: str = Field(min_length=1, max_length=254, description="The account username.")
    password: SecretStr = Field(min_length=1, description="The account password.")


class UserLoginResponse(BaseModel):
    """Access token and public user information returned after login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(ge=1, description="Token lifetime in seconds.")
    payload: UserInfo


class AdminLoginResponse(BaseModel):
    """Access token and public administrator information returned after login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(ge=1, description="Token lifetime in seconds.")
    payload: AdminInfo


class TokenClaims(BaseModel):
    """Validated claims required for an API access token."""

    sub: UUID
    role: Literal["user", "admin"]
    iat: int
    exp: int
    jti: UUID


__all__ = [
    "AdminLoginResponse",
    "LoginPayload",
    "TokenClaims",
    "UserLoginResponse",
]
