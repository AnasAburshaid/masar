"""Domain exceptions package."""

from masar.domain.exceptions.base import (
    AccessDeniedError,
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
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "AccessDeniedError",
    "AuthenticationError",
    "CorruptedStorageError",
    "DomainError",
    "EmptyFieldError",
    "EntityNotFoundError",
    "FieldLengthError",
    "InvalidCredentialsError",
    "InvalidIdError",
    "InvalidTokenError",
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
