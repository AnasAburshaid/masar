"""Note domain exceptions."""

from masar.domain.exceptions.base import EntityNotFoundError


class NoteNotFoundError(EntityNotFoundError):
    """Raised when a specific note is not found."""
