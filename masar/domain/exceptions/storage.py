"""Storage domain exception."""

from masar.domain.exceptions.base import DomainError


class StorageError(DomainError):
    """Raised when an error occurs during persistence storage operations."""
