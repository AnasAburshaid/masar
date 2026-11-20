"""Topic application service."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import (
    AccessDeniedError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Topic


class TopicService:
    """Service handling topics within sections."""

    def __init__(
        self,
        topic_repository: TopicRepository,
        section_repository: SectionRepository | None = None,
        note_repository: NoteRepository | None = None,
        journey_repository: JourneyRepository | None = None,
    ) -> None:
        self._topic_repository = topic_repository
        self._section_repository = section_repository
        self._note_repository = note_repository
        self._journey_repository = journey_repository

    def _verify_section_ownership(self, section_id: int, user_id: int | None) -> None:
        if self._section_repository:
            section = self._section_repository.get_by_id(section_id)
            if not section:
                raise SectionNotFoundError(f"Section with ID {section_id} was not found.")
            if user_id is not None and self._journey_repository:
                journey = self._journey_repository.get_by_id(section.journey_id)
                if journey and journey.user_id is not None and journey.user_id != user_id:
                    raise AccessDeniedError("You do not have permission to access topics in this section.")

    def create_topic(
        self,
        section_id: int,
        title: str,
        user_id: int | None = None,
    ) -> Topic:
        """Add a new topic to a section."""
        self._verify_section_ownership(section_id, user_id)
        topic = Topic(section_id=section_id, title=title)
        return self._topic_repository.add(topic)

    def list_topics(
        self,
        section_id: int,
        user_id: int | None = None,
    ) -> list[Topic]:
        """List all topics belonging to a section."""
        self._verify_section_ownership(section_id, user_id)
        return self._topic_repository.get_by_section_id(section_id)

    def get_topic(
        self,
        topic_id: int,
        user_id: int | None = None,
    ) -> Topic:
        """Retrieve a topic by ID."""
        topic = self._topic_repository.get_by_id(topic_id)
        if not topic:
            raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")
        self._verify_section_ownership(topic.section_id, user_id)
        return topic

    def rename_topic(
        self,
        topic_id: int,
        title: str,
        user_id: int | None = None,
    ) -> Topic:
        """Rename an existing topic."""
        topic = self.get_topic(topic_id, user_id=user_id)
        topic.rename(title)
        return self._topic_repository.update(topic)

    def set_topic_completion(
        self,
        topic_id: int,
        completed: bool,
        user_id: int | None = None,
    ) -> Topic:
        """Update completion status of a topic."""
        topic = self.get_topic(topic_id, user_id=user_id)
        topic.set_status(completed)
        return self._topic_repository.update(topic)

    def delete_topic(
        self,
        topic_id: int,
        user_id: int | None = None,
    ) -> None:
        """Delete a topic by ID and cascade delete attached notes."""
        self.get_topic(topic_id, user_id=user_id)

        if self._note_repository:
            self._note_repository.delete_by_topic_id(topic_id)

        deleted = self._topic_repository.delete(topic_id)
        if not deleted:
            raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")
