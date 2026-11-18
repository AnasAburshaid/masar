"""Repository abstractions package."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository

__all__ = ["JourneyRepository", "SectionRepository", "TopicRepository"]
