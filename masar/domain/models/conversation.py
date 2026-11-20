"""Conversation and message domain models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar

from masar.domain.exceptions.base import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)


@dataclass
class Conversation:
    """Represents a persistent conversation thread between a user and Masar AI."""

    user_id: int
    title: str = "New Conversation"
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_TITLE_LENGTH: ClassVar[int] = 150

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate conversation invariants."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Conversation title cannot be empty.")
        self.title = self.title.strip()
        if len(self.title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(
                f"Conversation title cannot exceed {self.MAX_TITLE_LENGTH} characters."
            )

    def update_title(self, new_title: str) -> None:
        """Update conversation title."""
        self.title = new_title
        self.updated_at = datetime.now(timezone.utc)
        self.validate()


@dataclass
class ConversationMessage:
    """Represents an individual message exchanged within a conversation."""

    conversation_id: int
    role: str
    content: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    VALID_ROLES: ClassVar[tuple[str, ...]] = ("user", "assistant", "system")

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate message invariants."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Message ID must be a positive integer.")
        if self.conversation_id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if not self.role or self.role.strip().lower() not in self.VALID_ROLES:
            raise ValidationError(
                f"Invalid message role '{self.role}'. Must be one of: {self.VALID_ROLES}"
            )
        self.role = self.role.strip().lower()
        if not self.content or not self.content.strip():
            raise EmptyFieldError("Message content cannot be empty.")
        self.content = self.content.strip()
