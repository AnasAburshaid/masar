"""Domain models for adaptive learning recommendations and knowledge gap analysis."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from masar.domain.exceptions.base import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)

VALID_RECOMMENDATION_TYPES = {
    "next_topic",
    "knowledge_gap",
    "review_refresher",
    "prerequisite",
    "journey_update",
}


@dataclass
class Recommendation:
    """Represents an actionable recommendation or pedagogical next step."""

    title: str
    reason: str
    recommendation_type: str = "next_topic"
    journey_id: Optional[int] = None
    journey_title: Optional[str] = None
    section_id: Optional[int] = None
    suggested_action: Optional[str] = None
    action_payload: Optional[dict[str, Any]] = None
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_TITLE_LENGTH: int = 250
    MAX_REASON_LENGTH: int = 2000

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate recommendation attributes."""
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Recommendation title cannot be empty.")

        clean_title = self.title.strip()
        if len(clean_title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(
                f"Recommendation title cannot exceed {self.MAX_TITLE_LENGTH} characters."
            )
        self.title = clean_title

        if not self.reason or not self.reason.strip():
            raise EmptyFieldError("Recommendation explanation/reason cannot be empty.")

        clean_reason = self.reason.strip()
        if len(clean_reason) > self.MAX_REASON_LENGTH:
            raise FieldLengthError(
                f"Recommendation reason cannot exceed {self.MAX_REASON_LENGTH} characters."
            )
        self.reason = clean_reason

        clean_type = self.recommendation_type.strip().lower()
        if clean_type not in VALID_RECOMMENDATION_TYPES:
            raise ValidationError(
                f"Invalid recommendation type '{self.recommendation_type}'. Allowed: {', '.join(sorted(VALID_RECOMMENDATION_TYPES))}."
            )
        self.recommendation_type = clean_type

        if self.journey_id is not None and self.journey_id <= 0:
            raise InvalidIdError("Journey ID must be a positive integer.")

        if self.section_id is not None and self.section_id <= 0:
            raise InvalidIdError("Section ID must be a positive integer.")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("Confidence score must be between 0.0 and 1.0.")


@dataclass
class KnowledgeGap:
    """Represents an identified missing skill, prerequisite, or conceptual gap."""

    topic_name: str
    description: str
    remedy: str
    related_journey_id: Optional[int] = None
    related_journey_title: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.topic_name or not self.topic_name.strip():
            raise EmptyFieldError("Knowledge gap topic name cannot be empty.")
        if not self.description or not self.description.strip():
            raise EmptyFieldError("Knowledge gap description cannot be empty.")
        if not self.remedy or not self.remedy.strip():
            raise EmptyFieldError("Knowledge gap remedy cannot be empty.")
        self.topic_name = self.topic_name.strip()
        self.description = self.description.strip()
        self.remedy = self.remedy.strip()


@dataclass
class AdaptiveLearningSummary:
    """Aggregate containing adaptive recommendations, gaps, and progress insights."""

    user_id: int
    total_completed_topics: int
    total_in_progress_topics: int
    active_journey_titles: list[str] = field(default_factory=list)
    knowledge_gaps: list[KnowledgeGap] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        if self.total_completed_topics < 0 or self.total_in_progress_topics < 0:
            raise ValidationError("Topic counts cannot be negative.")
