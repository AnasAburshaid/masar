"""Pydantic validation schemas for Topics."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TopicBaseSchema(BaseModel):
    """Shared Topic attributes."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class TopicCreateSchema(TopicBaseSchema):
    """Schema for creating a new Topic."""

    section_id: int = Field(..., gt=0, description="Parent section identifier")
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Non-empty topic title (max 100 characters)",
    )
    is_completed: bool = Field(
        default=False,
        description="Topic completion status",
    )
    order: int | None = Field(
        default=None,
        ge=0,
        description="Optional sequence order index",
    )


class TopicUpdateSchema(TopicBaseSchema):
    """Schema for updating an existing Topic."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated topic title",
    )
    is_completed: bool | None = Field(
        default=None,
        description="Updated completion status",
    )
    order: int | None = Field(
        default=None,
        ge=0,
        description="Updated sequence order index",
    )


class TopicResponseSchema(TopicBaseSchema):
    """Schema representing a Topic entity response."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    id: int = Field(..., gt=0, description="Positive entity identifier")
    section_id: int = Field(..., gt=0, description="Parent section identifier")
    title: str = Field(..., min_length=1, max_length=100)
    is_completed: bool = Field(default=False)
    created_at: datetime | str = Field(..., description="Creation timestamp")
