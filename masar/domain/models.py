"""Domain models for Masar."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import ValidationError


@dataclass
class Journey:
    """Represents a learning journey entity."""

    title: str
    description: str = ""
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate journey business rules."""
        if not self.title or not self.title.strip():
            raise ValidationError("Journey title cannot be empty.")
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else ""

    def update(self, title: str, description: str = "") -> None:
        """Update journey title and description."""
        self.title = title
        self.description = description
        self.validate()


@dataclass
class Section:
    """Represents a section grouping topics within a learning journey."""

    journey_id: int
    title: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate section business rules."""
        if not self.title or not self.title.strip():
            raise ValidationError("Section title cannot be empty.")
        self.title = self.title.strip()

    def rename(self, title: str) -> None:
        """Rename the section."""
        self.title = title
        self.validate()


@dataclass
class Topic:
    """Represents an individual subject to learn within a section."""

    section_id: int
    title: str
    is_completed: bool = False
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate topic business rules."""
        if not self.title or not self.title.strip():
            raise ValidationError("Topic title cannot be empty.")
        self.title = self.title.strip()

    def rename(self, title: str) -> None:
        """Rename the topic."""
        self.title = title
        self.validate()

    def mark_completed(self) -> None:
        """Mark topic as completed."""
        self.is_completed = True

    def mark_pending(self) -> None:
        """Mark topic as pending (not completed)."""
        self.is_completed = False

    def set_status(self, is_completed: bool) -> None:
        """Set topic completion status."""
        self.is_completed = bool(is_completed)
