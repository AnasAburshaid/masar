"""Infrastructure exceptions re-exported for convenience."""

from masar.domain.exceptions import (
    CorruptedStorageError,
    StorageAccessError,
    StorageError,
)

__all__ = ["CorruptedStorageError", "StorageAccessError", "StorageError"]
