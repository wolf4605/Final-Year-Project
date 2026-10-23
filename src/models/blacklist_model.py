"""Pydantic models for blacklist entries."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base_model import DatabaseModel


class BlacklistCreate(BaseModel):
    """Fields required to blacklist an email/contact pair."""

    email: str = Field(
        default=...,
        min_length=1,
        max_length=255,
        description="The email address to block.",
        examples=["blocked@example.com"],
    )
    contact: str = Field(
        default=...,
        min_length=1,
        max_length=50,
        description="The contact number to block.",
        examples=["+923001122344"],
    )
    duration: datetime | None = Field(
        default=None,
        description="When the blacklist entry expires; null means it does not expire.",
    )


class BlacklistUpdate(BaseModel):
    """Fields that can be changed on a blacklist entry."""

    email: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="The new email address to block.",
    )
    contact: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="The new contact number to block.",
    )
    duration: datetime | None = Field(
        default=None,
        description="The new expiry time; null means the entry does not expire.",
    )


class BlacklistInfo(DatabaseModel):
    """A blacklist record, including an optional expiry time."""

    id: UUID = Field(default=..., description="The blacklist entry's unique identifier.")
    email: str = Field(default=..., description="The blocked email address.")
    contact: str = Field(default=..., description="The blocked contact number.")
    duration: datetime | None = Field(default=..., description="When the entry expires, if it is temporary.")
    created_at: datetime | None = Field(default=..., description="When the blacklist entry was created.")


__all__ = ["BlacklistCreate", "BlacklistInfo", "BlacklistUpdate"]
