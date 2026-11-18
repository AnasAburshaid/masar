"""Topic repository abstraction."""

from abc import ABC, abstractmethod

from masar.domain.models import Topic


class TopicRepository(ABC):
    """Abstract repository interface for Topics."""

    @abstractmethod
    def add(self, topic: Topic) -> Topic:
        """Add a new topic to storage."""

    @abstractmethod
    def get_by_id(self, topic_id: int) -> Topic | None:
        """Retrieve a topic by ID."""

    @abstractmethod
    def get_by_section_id(self, section_id: int) -> list[Topic]:
        """Retrieve all topics belonging to a section."""

    @abstractmethod
    def update(self, topic: Topic) -> Topic:
        """Update an existing topic."""

    @abstractmethod
    def delete(self, topic_id: int) -> bool:
        """Delete a topic by ID."""

    @abstractmethod
    def delete_by_section_id(self, section_id: int) -> int:
        """Delete all topics belonging to a section."""
