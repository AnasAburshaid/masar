"""Journey domain exceptions."""

from masar.domain.exceptions.base import EntityNotFoundError


class JourneyNotFoundError(EntityNotFoundError):
    """Raised when a specific journey is not found."""
