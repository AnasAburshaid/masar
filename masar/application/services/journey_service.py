"""Journey application service."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import JourneyNotFoundError
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

    def create_journey(self, title: str, description: str = "") -> Journey:
        """Create a new learning journey."""
        journey = Journey(title=title, description=description)
        return self._repository.add(journey)

    def list_journeys(self) -> list[Journey]:
        """Return all learning journeys."""
        return self._repository.get_all()

    def get_journey(self, journey_id: int) -> Journey:
        """Retrieve a specific journey by ID."""
        journey = self._repository.get_by_id(journey_id)
        if not journey:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")
        return journey

    def update_journey(self, journey_id: int, title: str, description: str = "") -> Journey:
        """Update an existing learning journey's title and description."""
        journey = self.get_journey(journey_id)
        journey.update(title=title, description=description)
        return self._repository.update(journey)

    def delete_journey(self, journey_id: int) -> None:
        """Delete a journey by ID and cascade delete associated sections/topics/notes."""
        self.get_journey(journey_id)

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
