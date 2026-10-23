"""Pydantic models for user reports."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .base_model import DatabaseModel


class ReportCreate(BaseModel):
    """Fields required to submit a user report."""

    reported_by: UUID = Field(default=..., description="The identifier of the user submitting the report.")
    subject: str = Field(
        default=...,
        min_length=1,
        max_length=200,
        description="A short subject describing the report.",
        examples=["Incorrect account details", "Problem with a listing"],
    )
    content: str = Field(default=..., min_length=1, description="The details of the report.")


class ReportInfo(DatabaseModel):
    """A user report and its resolution details."""

    id: UUID = Field(default=..., description="The report's unique identifier.")
    reported_by: UUID = Field(default=..., description="The identifier of the user who submitted the report.")
    subject: str = Field(default=..., description="A short subject describing the report.")
    content: str = Field(default=..., description="The details of the report.")
    status: Literal["pending", "resolved"] = Field(default=..., description="The report's current resolution status.")
    created_at: datetime = Field(default=..., description="When the report was submitted.")
    resolved_at: datetime | None = Field(default=..., description="When the report was resolved, if applicable.")
    resolved_by: UUID | None = Field(default=..., description="The resolving administrator's ID, if applicable.")
    response: str | None = Field(default=..., description="The administrator's response, if resolved.")


__all__ = ["ReportCreate", "ReportInfo"]
