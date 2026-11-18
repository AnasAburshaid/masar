"""Domain exceptions package."""

from masar.domain.exceptions.base import (
    DomainError,
    EntityNotFoundError,
    ValidationError,
)
from masar.domain.exceptions.journey import JourneyNotFoundError
from masar.domain.exceptions.section import SectionNotFoundError
from masar.domain.exceptions.topic import TopicNotFoundError

__all__ = [
    "DomainError",
    "EntityNotFoundError",
    "JourneyNotFoundError",
    "SectionNotFoundError",
    "TopicNotFoundError",
    "ValidationError",
]
