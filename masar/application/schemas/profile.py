"""Pydantic validation schemas for user learning profile data."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileItemSchema(BaseModel):
    """Schema representing an individual skill, experience, or goal."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    user_id: int
    category: str
    name: str
    level: Optional[str] = None
    is_confirmed: bool
    source_type: str
    source_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProfileItemCreateSchema(BaseModel):
    """Schema for manually adding a new profile item."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    category: str = Field(
        ...,
        description="Category: 'skill', 'technology', 'language', 'experience', 'project', 'knowledge', or 'goal'",
    )
    name: str = Field(..., min_length=1, max_length=200, description="Name or title of the item")
    level: Optional[str] = Field(
        default=None,
        description="Optional mastery level: 'beginner', 'intermediate', 'advanced', 'expert'",
    )
    is_confirmed: bool = Field(
        default=True,
        description="Whether this item is confirmed by the user (defaults to True for manual entry)",
    )


class ProfileItemUpdateSchema(BaseModel):
    """Schema for editing an existing profile item."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = Field(default=None)
    level: Optional[str] = Field(default=None)
    is_confirmed: Optional[bool] = Field(default=None)


class ProfileBioUpdateSchema(BaseModel):
    """Schema for updating user bio."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    bio: str = Field(..., max_length=1000, description="Brief professional background summary")


class LearningProfileResponseSchema(BaseModel):
    """Schema representing the full learning profile of a user."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    user_id: int
    bio: str
    confirmed_items: list[ProfileItemSchema]
    inferred_items: list[ProfileItemSchema]
    total_items: int


class ProfileExtractionResponseSchema(BaseModel):
    """Response returned when items are extracted from a document or conversation."""

    extracted_items: list[ProfileItemSchema]
    source_type: str
    source_id: int
