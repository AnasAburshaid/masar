"""Learning profile domain models representing user skills, experience, and knowledge."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from masar.domain.exceptions.base import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)

VALID_CATEGORIES = {
    "skill",
    "technology",
    "language",
    "experience",
    "project",
    "knowledge",
    "goal",
}

VALID_LEVELS = {"beginner", "intermediate", "advanced", "expert"}
VALID_SOURCES = {"document", "conversation", "manual"}


@dataclass
class ProfileItem:
    """Represents a discrete skill, experience, goal, or knowledge entry in a user's profile."""

    user_id: int
    category: str
    name: str
    level: Optional[str] = None
    is_confirmed: bool = False
    source_type: str = "manual"
    source_id: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    MAX_NAME_LENGTH: int = 200

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate profile item invariants."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Profile item ID must be a positive integer.")

        if self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        if not self.name or not self.name.strip():
            raise EmptyFieldError("Profile item name cannot be empty.")

        clean_name = self.name.strip()
        if len(clean_name) > self.MAX_NAME_LENGTH:
            raise FieldLengthError(
                f"Profile item name cannot exceed {self.MAX_NAME_LENGTH} characters."
            )
        self.name = clean_name

        clean_category = self.category.strip().lower()
        if clean_category not in VALID_CATEGORIES:
            raise ValidationError(
                f"Invalid profile category '{self.category}'. Allowed categories: {', '.join(sorted(VALID_CATEGORIES))}."
            )
        self.category = clean_category

        if self.level is not None:
            clean_level = self.level.strip().lower()
            if clean_level not in VALID_LEVELS:
                raise ValidationError(
                    f"Invalid skill level '{self.level}'. Allowed levels: {', '.join(sorted(VALID_LEVELS))}."
                )
            self.level = clean_level

        clean_source = self.source_type.strip().lower()
        if clean_source not in VALID_SOURCES:
            raise ValidationError(
                f"Invalid source type '{self.source_type}'. Allowed sources: {', '.join(sorted(VALID_SOURCES))}."
            )
        self.source_type = clean_source

        if self.source_id is not None and self.source_id <= 0:
            raise InvalidIdError("Source ID must be a positive integer.")

    def confirm(self) -> None:
        """Mark an AI-inferred profile item as user-confirmed."""
        self.is_confirmed = True
        self.updated_at = datetime.now(timezone.utc)

    def update(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        is_confirmed: Optional[bool] = None,
    ) -> None:
        """Update profile item attributes."""
        if name is not None:
            self.name = name
        if category is not None:
            self.category = category
        if level is not None:
            self.level = level
        if is_confirmed is not None:
            self.is_confirmed = is_confirmed
        self.validate()
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class LearningProfile:
    """Aggregate representing the user's complete knowledge, skills, and goals profile."""

    user_id: int
    bio: str = ""
    items: list[ProfileItem] = field(default_factory=list)

    @property
    def confirmed_items(self) -> list[ProfileItem]:
        """Return only verified, user-confirmed profile items."""
        return [i for i in self.items if i.is_confirmed]

    @property
    def inferred_items(self) -> list[ProfileItem]:
        """Return AI-inferred items awaiting user review."""
        return [i for i in self.items if not i.is_confirmed]

    @property
    def total_items(self) -> int:
        """Return total count of profile items."""
        return len(self.items)

    def get_by_category(self, category: str, confirmed_only: bool = False) -> list[ProfileItem]:
        """Filter profile items by category."""
        target = category.lower().strip()
        pool = self.confirmed_items if confirmed_only else self.items
        return [i for i in pool if i.category == target]
