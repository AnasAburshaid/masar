"""Conversation domain exceptions."""

from masar.domain.exceptions.base import (
    AccessDeniedError,
    EmptyFieldError,
    EntityNotFoundError,
    ValidationError,
)


class ConversationNotFoundError(EntityNotFoundError):
    """Raised when a specific conversation cannot be found."""


class ConversationAccessDeniedError(AccessDeniedError):
    """Raised when an authenticated user attempts to access another user's conversation."""


class InvalidMessageRoleError(ValidationError):
    """Raised when an unsupported role is specified for a conversation message."""


class EmptyMessageError(EmptyFieldError):
    """Raised when message content is blank or contains only whitespace."""
