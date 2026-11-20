"""Pydantic validation schemas for raw storage persistence records."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class StorageRecordBase(BaseModel):
    """Base schema for stored JSON persistence records."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")


class StorageJourneyRecord(StorageRecordBase):
    """Schema validating a persisted Journey record."""

    id: int = Field(..., gt=0, description="Unique positive journey ID")
    user_id: int | None = Field(default=None, description="Optional owner user ID")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    created_at: str | None = Field(default=None)


class StorageSectionRecord(StorageRecordBase):
    """Schema validating a persisted Section record."""

    id: int = Field(..., gt=0, description="Unique positive section ID")
    journey_id: int = Field(..., gt=0, description="Parent journey ID")
    title: str = Field(..., min_length=1, max_length=200)
    order: int = Field(default=0, ge=0)
    created_at: str | None = Field(default=None)


class StorageTopicRecord(StorageRecordBase):
    """Schema validating a persisted Topic record."""

    id: int = Field(..., gt=0, description="Unique positive topic ID")
    section_id: int = Field(..., gt=0, description="Parent section ID")
    title: str = Field(..., min_length=1, max_length=200)
    order: int = Field(default=0, ge=0)
    completed: bool = Field(default=False)
    is_completed: bool | None = Field(default=None)
    created_at: str | None = Field(default=None)


class StorageNoteRecord(StorageRecordBase):
    """Schema validating a persisted Note record."""

    id: int = Field(..., gt=0, description="Unique positive note ID")
    topic_id: int = Field(..., gt=0, description="Parent topic ID")
    content: str = Field(..., min_length=1, max_length=5000)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)


class StorageUserRecord(StorageRecordBase):
    """Schema validating a persisted User record."""

    id: int = Field(..., gt=0, description="Unique positive user ID")
    email: str = Field(..., min_length=3, max_length=255)
    hashed_password: str = Field(..., min_length=1)
    is_active: bool = Field(default=True)
    created_at: str | None = Field(default=None)


class StorageDataSchema(BaseModel):
    """Schema validating the full top-level JSON storage structure."""

    model_config = ConfigDict(extra="allow")

    users: list[StorageUserRecord] = Field(default_factory=list)
    journeys: list[StorageJourneyRecord] = Field(default_factory=list)
    sections: list[StorageSectionRecord] = Field(default_factory=list)
    topics: list[StorageTopicRecord] = Field(default_factory=list)
    notes: list[StorageNoteRecord] = Field(default_factory=list)


def validate_storage_data(data: dict[str, Any]) -> StorageDataSchema:
    """Validate raw loaded JSON dictionary against the StorageDataSchema."""
    return StorageDataSchema.model_validate(data)
