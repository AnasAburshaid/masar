"""Storage domain exception."""

from masar.domain.exceptions.base import DomainError


class StorageError(DomainError):
    """Raised when an error occurs during persistence storage operations."""


class CorruptedStorageError(StorageError):
    """Raised when stored data cannot be parsed or has an invalid structure."""


class StorageAccessError(StorageError):
    """Raised when storage files cannot be read or written due to OS/file access errors."""
