"""Domain exceptions package."""

from masar.domain.exceptions.base import (
    DomainError,
    EmptyFieldError,
    EntityNotFoundError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)
from masar.domain.exceptions.journey import JourneyNotFoundError
from masar.domain.exceptions.note import NoteNotFoundError
from masar.domain.exceptions.section import SectionNotFoundError
from masar.domain.exceptions.storage import (
    CorruptedStorageError,
    StorageAccessError,
    StorageError,
)
from masar.domain.exceptions.topic import TopicNotFoundError
from masar.domain.exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "CorruptedStorageError",
    "DomainError",
    "EmptyFieldError",
    "EntityNotFoundError",
    "FieldLengthError",
    "InvalidIdError",
    "JourneyNotFoundError",
    "NoteNotFoundError",
    "SectionNotFoundError",
    "StorageAccessError",
    "StorageError",
    "TopicNotFoundError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "ValidationError",
]
