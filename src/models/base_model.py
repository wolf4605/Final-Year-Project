"""Shared configuration for models loaded from database records."""

from pydantic import BaseModel, ConfigDict


class DatabaseModel(BaseModel):
    """Common configuration for models created from database records."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")


__all__ = ["DatabaseModel"]
