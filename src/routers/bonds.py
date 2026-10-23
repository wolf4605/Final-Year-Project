"""
* Project Name: BONDVAULT PK

* Description: 

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 19:09:05

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 19:09:26

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from .. import models
from ..utilities.auth_dependencies import get_current_user

router = APIRouter(
    prefix = "/bonds",
)


@router.get(
    "/me",
    response_model= models.UserInfo,
    summary="Get the authenticated user's profile",
)
async def get_user_info(
    user_info: Annotated[models.UserInfo, Depends(get_current_user)],
    
) -> models.UserInfo:
    """Return the authenticated user's profile without a separate user ID."""
    return user_info
