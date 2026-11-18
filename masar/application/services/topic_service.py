"""Topic application service."""

from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import SectionNotFoundError, TopicNotFoundError
from masar.domain.models import Topic


class TopicService:
    """Service handling topics within sections."""

    def __init__(
        self,
        topic_repository: TopicRepository,
        section_repository: SectionRepository | None = None,
    ) -> None:
        self._topic_repository = topic_repository
        self._section_repository = section_repository

    def create_topic(self, section_id: int, title: str) -> Topic:
        """Add a new topic to a section."""
        if self._section_repository:
            section = self._section_repository.get_by_id(section_id)
            if not section:
                raise SectionNotFoundError(f"Section with ID {section_id} was not found.")

        topic = Topic(section_id=section_id, title=title)
        return self._topic_repository.add(topic)

    def list_topics(self, section_id: int) -> list[Topic]:
        """List all topics belonging to a section."""
        if self._section_repository:
            section = self._section_repository.get_by_id(section_id)
            if not section:
                raise SectionNotFoundError(f"Section with ID {section_id} was not found.")

        return self._topic_repository.get_by_section_id(section_id)

    def get_topic(self, topic_id: int) -> Topic:
        """Retrieve a topic by ID."""
        topic = self._topic_repository.get_by_id(topic_id)
        if not topic:
            raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")
        return topic

    def rename_topic(self, topic_id: int, title: str) -> Topic:
        """Rename an existing topic."""
        topic = self.get_topic(topic_id)
        topic.rename(title)
        return self._topic_repository.update(topic)

    def set_topic_completion(self, topic_id: int, completed: bool) -> Topic:
        """Update completion status of a topic."""
        topic = self.get_topic(topic_id)
        topic.set_status(completed)
        return self._topic_repository.update(topic)

    def delete_topic(self, topic_id: int) -> None:
        """Delete a topic by ID."""
        deleted = self._topic_repository.delete(topic_id)
        if not deleted:
            raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")
