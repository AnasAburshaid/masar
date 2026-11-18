"""Section domain model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)


@dataclass
class Section:
    """Represents a section grouping topics within a learning journey."""

    journey_id: int
    title: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_TITLE_LENGTH: int = 100

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate section business rules."""
        if self.journey_id <= 0:
            raise InvalidIdError("Journey ID must be a positive integer.")
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Section ID must be a positive integer.")
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Section title cannot be empty.")
        self.title = self.title.strip()
        if len(self.title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(f"Section title cannot exceed {self.MAX_TITLE_LENGTH} characters.")

    def rename(self, title: str) -> None:
        """Rename the section."""
        self.title = title
        self.validate()

    @property
    def is_persisted(self) -> bool:
        """Return True if section has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        label = f"Section {self.id}" if self.is_persisted else "Section New"
        return f"[{label}] {self.title}"
