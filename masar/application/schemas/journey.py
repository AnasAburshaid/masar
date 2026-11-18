"""Pydantic validation schemas for Learning Journeys."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JourneyBaseSchema(BaseModel):
    """Shared Journey attributes."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class JourneyCreateSchema(JourneyBaseSchema):
    """Schema for creating a new Learning Journey."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Non-empty journey title (max 100 characters)",
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional journey description (max 1000 characters)",
    )


class JourneyUpdateSchema(JourneyBaseSchema):
    """Schema for updating an existing Learning Journey."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated journey title",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Updated journey description",
    )


class JourneyResponseSchema(JourneyBaseSchema):
    """Schema representing a Journey entity response."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    id: int = Field(..., gt=0, description="Positive entity identifier")
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    created_at: datetime | str = Field(..., description="Creation timestamp")
