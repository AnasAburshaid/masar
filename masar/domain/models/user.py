"""User domain model."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class User:
    """Represents a registered user in Masar."""

    email: str
    hashed_password: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    MAX_EMAIL_LENGTH: int = 255

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate user business rules."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        if not self.email or not self.email.strip():
            raise EmptyFieldError("Email cannot be empty.")

        self.email = self.email.strip().lower()
        if len(self.email) > self.MAX_EMAIL_LENGTH:
            raise FieldLengthError(f"Email cannot exceed {self.MAX_EMAIL_LENGTH} characters.")

        if not EMAIL_REGEX.match(self.email):
            raise ValidationError("Invalid email address format.")

        if not self.hashed_password or not self.hashed_password.strip():
            raise EmptyFieldError("Hashed password cannot be empty.")

    @property
    def is_persisted(self) -> bool:
        """Return True if user has been persisted with an assigned ID."""
        return self.id is not None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        prefix = f"User {self.id}" if self.is_persisted else "User New"
        status = "Active" if self.is_active else "Inactive"
        return f"[{prefix}] {self.email} ({status})"
