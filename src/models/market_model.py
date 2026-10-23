"""Pydantic models for market listings."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .base_model import DatabaseModel


class MarketCreate(BaseModel):
    """Fields required to publish a market listing."""

    posted_by: UUID = Field(default=..., description="The identifier of the user posting the listing.")
    title: str = Field(
        default=...,
        min_length=1,
        max_length=150,
        description="The listing title.",
        examples=["Prize bonds available", "Looking to buy prize bonds"],
    )
    description: str | None = Field(default=None, description="Optional details about the listing.")
    price: int = Field(default=..., ge=0, description="The listing price in PKR.")
    category: Literal["buy", "sell"] = Field(
        default=...,
        description="Whether the listing is a buy or sell offer.",
        examples=["buy", "sell"],
    )


class MarketInfo(DatabaseModel):
    """A market listing record."""

    id: UUID = Field(default=..., description="The listing's unique identifier.")
    posted_by: UUID = Field(default=..., description="The identifier of the user who posted the listing.")
    title: str = Field(default=..., description="The listing title.")
    description: str | None = Field(default=..., description="Optional details about the listing.")
    price: int = Field(default=..., ge=0, description="The listing price in PKR.")
    category: Literal["buy", "sell"] = Field(default=..., description="Whether the listing is a buy or sell offer.")
    created_at: datetime = Field(default=..., description="When the listing was created.")


class MarketUpdate(BaseModel):
    """Fields that can be changed on a market listing."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="The listing's new title.",
    )
    description: str | None = Field(default=None, description="The listing's new details.")
    price: int | None = Field(default=None, ge=0, description="The listing's new price in PKR.")
    category: Literal["buy", "sell"] | None = Field(
        default=None,
        description="The listing's new buy or sell category.",
    )


__all__ = ["MarketCreate", "MarketInfo", "MarketUpdate"]
