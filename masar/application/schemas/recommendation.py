"""Pydantic schemas for adaptive learning recommendations and knowledge gap analysis."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationSchema(BaseModel):
    """Schema representing an actionable adaptive learning recommendation."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    title: str = Field(..., description="Actionable recommendation title")
    reason: str = Field(..., description="Pedagogical explanation of why this is recommended")
    recommendation_type: str = Field(
        default="next_topic",
        description="Type: 'next_topic', 'knowledge_gap', 'review_refresher', 'prerequisite', 'journey_update'",
    )
    journey_id: Optional[int] = Field(default=None, description="Associated journey ID if applicable")
    journey_title: Optional[str] = Field(default=None, description="Title of the associated journey")
    section_id: Optional[int] = Field(default=None, description="Associated section ID if applicable")
    suggested_action: Optional[str] = Field(
        default=None, description="Recommended platform action (e.g., 'study_next', 'create_topic')"
    )
    action_payload: Optional[dict[str, Any]] = Field(
        default=None, description="Optional parameters for suggested action"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime


class KnowledgeGapSchema(BaseModel):
    """Schema representing an identified knowledge or prerequisite gap."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    topic_name: str
    description: str
    remedy: str
    related_journey_id: Optional[int] = None
    related_journey_title: Optional[str] = None


class AdaptiveLearningSummarySchema(BaseModel):
    """Schema representing the user's complete adaptive learning analysis and recommendations."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    user_id: int
    total_completed_topics: int
    total_in_progress_topics: int
    active_journey_titles: list[str]
    knowledge_gaps: list[KnowledgeGapSchema]
    recommendations: list[RecommendationSchema]
    generated_at: datetime
