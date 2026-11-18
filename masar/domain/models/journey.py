"""Journey domain model."""

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

    @property
    def is_persisted(self) -> bool:
        """Return True if entity has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        prefix = f"[{self.id}]" if self.is_persisted else "[New]"
        return f"{prefix} {self.title}"
