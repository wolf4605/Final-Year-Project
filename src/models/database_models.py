"""
* Project Name: BONDVAULT PK

* Description: Pydantic models for database records and partial updates.

* Author: Wolf4605
* Email: mab4605@gmail.com

* Date: 2026-10-23 07:22:37

* Last Modified by: Wolf4605
* Last Modified time: 2026-10-23 07:42:18

* License: MIT
* Copyright© BondVault PK. All rights reserved.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..configs import PrizeBondDenominations


class DatabaseModel(BaseModel):
    """Common configuration for models created from database records."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AdminInfo(DatabaseModel):
    """Public administrator fields returned by database operations."""

    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    contact: str | None
    created_at: datetime
    is_superuser: bool


class AdminUpdate(BaseModel):
    """Fields that can be changed on an administrator account."""

    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    contact: str | None = None
    is_superuser: bool | None = None


class UserInfo(DatabaseModel):
    """Public user fields returned by database operations."""

    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    contact: str | None
    created_at: datetime
    is_verified: bool
    verified_by: UUID | None
    last_login: datetime | None


class UserUpdate(BaseModel):
    """Fields that can be changed on a user account."""

    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    contact: str | None = None


class BondlistUpdate(BaseModel):
    """Fields that can be changed on a bondlist."""

    denomination: PrizeBondDenominations | None = None


class BondLocation(DatabaseModel):
    """A bond's list and owner, with the applicable denomination."""

    bond_number: str
    bondlist_id: UUID
    denomination: PrizeBondDenominations
    user_id: UUID


class DrawlistUpdate(BaseModel):
    """Mutable prize-result fields for an existing drawlist."""

    first_winner: str | None = None
    first_prize: int | None = Field(default=None, ge=0)
    second_winner: list[str] | None = None
    second_prize: int | None = Field(default=None, ge=0)
    other_winners: list[str] | None = None
    other_prize: int | None = Field(default=None, ge=0)


class MarketCreate(BaseModel):
    """Fields required to publish a market listing."""

    posted_by: UUID
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: int = Field(ge=0)
    category: Literal["buy", "sell"]


class MarketInfo(DatabaseModel):
    """A market listing record."""

    id: UUID
    posted_by: UUID
    title: str
    description: str | None
    price: int
    category: Literal["buy", "sell"]
    created_at: datetime


class MarketUpdate(BaseModel):
    """Fields that can be changed on a market listing."""

    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: int | None = Field(default=None, ge=0)
    category: Literal["buy", "sell"] | None = None


class ReportCreate(BaseModel):
    """Fields required to submit a user report."""

    reported_by: UUID
    subject: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class ReportInfo(DatabaseModel):
    """A user report and its resolution details."""

    id: UUID
    reported_by: UUID
    subject: str
    content: str
    status: Literal["pending", "resolved"]
    created_at: datetime
    resolved_at: datetime | None
    resolved_by: UUID | None
    response: str | None


class BlacklistCreate(BaseModel):
    """Fields required to blacklist an email/contact pair."""

    email: str = Field(min_length=1, max_length=255)
    contact: str = Field(min_length=1, max_length=50)
    duration: datetime | None = None


class BlacklistUpdate(BaseModel):
    """Fields that can be changed on a blacklist entry."""

    email: str | None = Field(default=None, min_length=1, max_length=255)
    contact: str | None = Field(default=None, min_length=1, max_length=50)
    duration: datetime | None = None


class BlacklistInfo(DatabaseModel):
    """A blacklist record, including an optional expiry time."""

    id: UUID
    email: str
    contact: str
    duration: datetime | None
    created_at: datetime | None
