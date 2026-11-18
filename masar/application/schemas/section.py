"""Pydantic validation schemas for Sections."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SectionBaseSchema(BaseModel):
    """Shared Section attributes."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class SectionCreateSchema(SectionBaseSchema):
    """Schema for creating a new Section."""

    journey_id: int = Field(..., gt=0, description="Parent journey identifier")
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Non-empty section title (max 100 characters)",
    )
    order: int | None = Field(
        default=None,
        ge=0,
        description="Optional sequence order index",
    )


class SectionUpdateSchema(SectionBaseSchema):
    """Schema for updating an existing Section."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated section title",
    )
    order: int | None = Field(
        default=None,
        ge=0,
        description="Updated sequence order index",
    )


class SectionResponseSchema(SectionBaseSchema):
    """Schema representing a Section entity response."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    id: int = Field(..., gt=0, description="Positive entity identifier")
    journey_id: int = Field(..., gt=0, description="Parent journey identifier")
    title: str = Field(..., min_length=1, max_length=100)
    created_at: datetime | str = Field(..., description="Creation timestamp")
