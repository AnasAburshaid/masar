"""Journey application service."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import AccessDeniedError, JourneyNotFoundError
from masar.domain.models import Journey


class JourneyService:
    """Service handling learning journey use cases."""

    def __init__(
        self,
        repository: JourneyRepository,
        section_repository: SectionRepository | None = None,
        topic_repository: TopicRepository | None = None,
        note_repository: NoteRepository | None = None,
    ) -> None:
        self._repository = repository
        self._section_repository = section_repository
        self._topic_repository = topic_repository
        self._note_repository = note_repository

    def create_journey(
        self,
        title: str,
        description: str = "",
        user_id: int | None = None,
    ) -> Journey:
        """Create a new learning journey."""
        journey = Journey(title=title, description=description, user_id=user_id)
        return self._repository.add(journey)

    def list_journeys(self, user_id: int | None = None) -> list[Journey]:
        """Return learning journeys, filtered by user_id if provided."""
        if user_id is not None:
            return self._repository.get_by_user_id(user_id)
        return self._repository.get_all()

    def get_journey(self, journey_id: int, user_id: int | None = None) -> Journey:
        """Retrieve a specific journey by ID, ensuring ownership matches if user_id is provided."""
        journey = self._repository.get_by_id(journey_id)
        if not journey:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")
        if user_id is not None and journey.user_id is not None and journey.user_id != user_id:
            raise AccessDeniedError("You do not have permission to access this journey.")
        return journey

    def update_journey(
        self,
        journey_id: int,
        title: str,
        description: str = "",
        user_id: int | None = None,
    ) -> Journey:
        """Update an existing learning journey's title and description."""
        journey = self.get_journey(journey_id, user_id=user_id)
        journey.update(title=title, description=description)
        return self._repository.update(journey)

    def delete_journey(self, journey_id: int, user_id: int | None = None) -> None:
        """Delete a journey by ID and cascade delete associated sections/topics/notes."""
        self.get_journey(journey_id, user_id=user_id)

        # Cascade delete sections, topics, and notes if repositories are attached
        if self._section_repository:
            sections = self._section_repository.get_by_journey_id(journey_id)
            for section in sections:
                if self._topic_repository and section.id is not None:
                    if self._note_repository:
                        topics = self._topic_repository.get_by_section_id(section.id)
                        for topic in topics:
                            if topic.id is not None:
                                self._note_repository.delete_by_topic_id(topic.id)
                    self._topic_repository.delete_by_section_id(section.id)
                if section.id is not None:
                    self._section_repository.delete(section.id)

        deleted = self._repository.delete(journey_id)
        if not deleted:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")
