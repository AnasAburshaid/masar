"""Note domain model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import ValidationError


@dataclass
class Note:
    """Represents a note attached to a learning topic."""

    topic_id: int
    content: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate note business rules."""
        if not self.content or not self.content.strip():
            raise ValidationError("Note content cannot be empty.")
        self.content = self.content.strip()

    def update(self, content: str) -> None:
        """Update note content."""
        self.content = content
        self.validate()
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_persisted(self) -> bool:
        """Return True if note has been persisted with an assigned ID."""
        return self.id is not None

    @property
    def is_edited(self) -> bool:
        """Return True if note has been updated since creation."""
        return self.updated_at is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        prefix = f"Note {self.id}" if self.is_persisted else "Note New"
        return f"[{prefix}] {self.content}"
