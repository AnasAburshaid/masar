"""User domain exceptions."""

from masar.domain.exceptions.base import DomainError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    """Raised when a specific user is not found."""


class UserAlreadyExistsError(DomainError):
    """Raised when attempting to create a user with an already registered email."""
