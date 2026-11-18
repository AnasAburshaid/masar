"""Section domain model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import ValidationError


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

    @property
    def is_persisted(self) -> bool:
        """Return True if section has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        label = f"Section {self.id}" if self.is_persisted else "Section New"
        return f"[{label}] {self.title}"
