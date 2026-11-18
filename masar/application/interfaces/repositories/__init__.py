"""Repository abstractions package."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository

__all__ = [
    "JourneyRepository",
    "NoteRepository",
    "SectionRepository",
    "TopicRepository",
]
