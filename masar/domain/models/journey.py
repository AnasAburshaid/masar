"""Journey domain model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)


@dataclass
class Journey:
    """Represents a learning journey entity."""

    title: str
    description: str = ""
    id: int | None = None
    user_id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_TITLE_LENGTH: int = 100
    MAX_DESCRIPTION_LENGTH: int = 1000

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate journey business rules."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Journey ID must be a positive integer.")
        if self.user_id is not None and self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Journey title cannot be empty.")
        self.title = self.title.strip()
        if len(self.title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(f"Journey title cannot exceed {self.MAX_TITLE_LENGTH} characters.")
        self.description = self.description.strip() if self.description else ""
        if len(self.description) > self.MAX_DESCRIPTION_LENGTH:
            raise FieldLengthError(f"Journey description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters.")

    def update(self, title: str, description: str = "") -> None:
        """Update journey title and description."""
        self.title = title
        self.description = description
        self.validate()

    @property
    def is_persisted(self) -> bool:
        """Return True if entity has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        prefix = f"[{self.id}]" if self.is_persisted else "[New]"
        return f"{prefix} {self.title}"
