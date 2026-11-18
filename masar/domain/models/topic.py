"""Topic domain model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)


@dataclass
class Topic:
    """Represents an individual subject to learn within a section."""

    section_id: int
    title: str
    is_completed: bool = False
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_TITLE_LENGTH: int = 100

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate topic business rules."""
        if self.section_id <= 0:
            raise InvalidIdError("Section ID must be a positive integer.")
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Topic ID must be a positive integer.")
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Topic title cannot be empty.")
        self.title = self.title.strip()
        if len(self.title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(f"Topic title cannot exceed {self.MAX_TITLE_LENGTH} characters.")

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

    def toggle_status(self) -> bool:
        """Toggle completion status and return new status."""
        self.is_completed = not self.is_completed
        return self.is_completed

    @property
    def is_persisted(self) -> bool:
        """Return True if topic has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        status_box = "[✓]" if self.is_completed else "[ ]"
        prefix = f"Topic {self.id}" if self.is_persisted else "Topic New"
        return f"[{prefix}] {status_box} {self.title}"
