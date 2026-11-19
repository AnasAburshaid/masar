"""Pydantic validation schemas for Learning Progress."""

from pydantic import BaseModel, ConfigDict, Field


class SectionProgressSchema(BaseModel):
    """Schema representing progress details for a section."""

    model_config = ConfigDict(extra="forbid")

    section_id: int = Field(..., gt=0, description="Section identifier")
    title: str = Field(..., description="Section title")
    completed_topics: int = Field(..., ge=0, description="Number of completed topics")
    total_topics: int = Field(..., ge=0, description="Total number of topics in this section")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Completion percentage (0.0 - 100.0)")
    is_complete: bool = Field(..., description="Whether all topics in section are completed")


class JourneyProgressSchema(BaseModel):
    """Schema representing detailed progress for a learning journey."""

    model_config = ConfigDict(extra="forbid")

    journey_id: int = Field(..., gt=0, description="Journey identifier")
    title: str = Field(..., description="Journey title")
    completed_topics: int = Field(..., ge=0, description="Number of completed topics across journey")
    total_topics: int = Field(..., ge=0, description="Total topics across journey")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Overall completion percentage")
    is_complete: bool = Field(..., description="Whether entire journey is completed")
    sections: list[SectionProgressSchema] = Field(
        default_factory=list,
        description="Progress breakdown per section",
    )
