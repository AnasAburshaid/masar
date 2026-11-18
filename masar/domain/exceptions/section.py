"""Section domain exceptions."""

from masar.domain.exceptions.base import EntityNotFoundError


class SectionNotFoundError(EntityNotFoundError):
    """Raised when a specific section is not found."""
