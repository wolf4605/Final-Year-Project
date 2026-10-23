<<<<<<< HEAD
"""
* Project Name: BONDVAULT PK

* Description: Request and response models for user and administrator authentication.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 11:19:18

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 11:55:00

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
=======
"""Request and response models for user and administrator authentication."""
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a

from typing import Literal
from uuid import UUID

<<<<<<< HEAD
from pydantic import BaseModel
=======
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
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a


class TokenClaims(BaseModel):
    """Validated claims required for an API access token."""

    sub: UUID
    role: Literal["user", "admin"]
    iat: int
    exp: int
    jti: UUID


__all__ = [
<<<<<<< HEAD
    "TokenClaims",
=======
    "AdminLoginResponse",
    "LoginPayload",
    "TokenClaims",
    "UserLoginResponse",
>>>>>>> 650ab09f5fa893458b064e3f3afe2646e080165a
]
