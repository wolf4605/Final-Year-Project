"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 19:26:49

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 19:26:51

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from typing import Literal

from fastapi import status
from pydantic import BaseModel, Field

from .. import models


class BaseResponse(BaseModel):
    """The Base Response for all the responses."""
    status_code: int = Field(default=status.HTTP_200_OK, description= "The status code for the request.")
    message: str|None = Field(default = None, description = "The message to attach along with the response.")

class UserInfoResponse(BaseResponse):
    """Response for sending the minimal user info."""
    user_info: models.UserInfo
    """The user information feched from the database."""


class UserLoginResponse(BaseModel):
    """Access token and public user information returned after login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(ge=1, description="Token lifetime in seconds.")
    payload: models.UserInfo

class AdminLoginResponse(BaseModel):
    """Access token and public administrator information returned after login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(ge=1, description="Token lifetime in seconds.")
    payload: models.AdminInfo

    