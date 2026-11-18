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
