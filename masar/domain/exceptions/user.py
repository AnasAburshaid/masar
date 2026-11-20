"""User domain exceptions."""

from masar.domain.exceptions.base import DomainError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    """Raised when a specific user is not found."""


class UserAlreadyExistsError(DomainError):
    """Raised when attempting to create a user with an already registered email."""


class AuthenticationError(DomainError):
    """Base exception for authentication failures."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when user credentials (email or password) are incorrect."""


class InvalidTokenError(AuthenticationError):
    """Raised when an authentication token is malformed, invalid, or expired."""

