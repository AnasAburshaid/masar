"""Application interfaces package."""

from masar.application.interfaces.repositories import (
    JourneyRepository,
    SectionRepository,
    TopicRepository,
)

__all__ = ["JourneyRepository", "SectionRepository", "TopicRepository"]
