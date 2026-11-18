"""Topic domain exceptions."""

from masar.domain.exceptions.base import EntityNotFoundError


class TopicNotFoundError(EntityNotFoundError):
    """Raised when a specific topic is not found."""
