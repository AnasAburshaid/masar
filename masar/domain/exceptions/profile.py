"""Domain exceptions for Learning Knowledge Profile operations."""

from masar.domain.exceptions.base import (
    AccessDeniedError,
    DomainError,
    EntityNotFoundError,
)


class ProfileError(DomainError):
    """Base exception for learning profile operations."""


class ProfileItemNotFoundError(EntityNotFoundError, ProfileError):
    """Raised when a specific profile item cannot be found."""


class ProfileAccessDeniedError(AccessDeniedError, ProfileError):
    """Raised when a user attempts to access or modify another user's profile item."""
