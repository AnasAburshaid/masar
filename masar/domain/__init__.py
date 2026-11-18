"""Domain layer containing core business entities and rules."""

from masar.domain.exceptions import (
    DomainError,
    EntityNotFoundError,
    JourneyNotFoundError,
    NoteNotFoundError,
    SectionNotFoundError,
    StorageError,
    TopicNotFoundError,
    ValidationError,
)
from masar.domain.models import Journey, Note, Progress, Section, Topic
from masar.domain.types import (
    EntityId,
    JourneyId,
    NoteId,
    SectionId,
    SerializedData,
    Timestamp,
    TopicId,
)

__all__ = [
    "DomainError",
    "EntityId",
    "EntityNotFoundError",
    "Journey",
    "JourneyId",
    "JourneyNotFoundError",
    "Note",
    "NoteId",
    "NoteNotFoundError",
    "Progress",
    "Section",
    "SectionId",
    "SectionNotFoundError",
    "SerializedData",
    "StorageError",
    "Timestamp",
    "Topic",
    "TopicId",
    "TopicNotFoundError",
    "ValidationError",
]
