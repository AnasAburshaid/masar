"""Pydantic validation schemas for Topic Notes."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NoteBaseSchema(BaseModel):
    """Shared Note attributes."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class NoteCreateSchema(NoteBaseSchema):
    """Schema for creating a new Note attached to a Topic."""

    topic_id: int = Field(..., gt=0, description="Parent topic identifier")
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Non-empty note body content (max 5000 characters)",
    )


class NoteUpdateSchema(NoteBaseSchema):
    """Schema for updating an existing Note."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Updated non-empty note content",
    )


class NoteResponseSchema(NoteBaseSchema):
    """Schema representing a Note entity response."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    id: int = Field(..., gt=0, description="Positive entity identifier")
    topic_id: int = Field(..., gt=0, description="Parent topic identifier")
    content: str = Field(..., min_length=1, max_length=5000)
    created_at: datetime | str = Field(..., description="Creation timestamp")
