"""Section application service."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import JourneyNotFoundError, SectionNotFoundError
from masar.domain.models import Section


class SectionService:
    """Service handling sections within learning journeys."""

    def __init__(
        self,
        section_repository: SectionRepository,
        journey_repository: JourneyRepository | None = None,
        topic_repository: TopicRepository | None = None,
    ) -> None:
        self._section_repository = section_repository
        self._journey_repository = journey_repository
        self._topic_repository = topic_repository

    def create_section(self, journey_id: int, title: str) -> Section:
        """Create a new section inside a learning journey."""
        if self._journey_repository:
            journey = self._journey_repository.get_by_id(journey_id)
            if not journey:
                raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")

        section = Section(journey_id=journey_id, title=title)
        return self._section_repository.add(section)

    def list_sections(self, journey_id: int) -> list[Section]:
        """List all sections belonging to a specific journey."""
        if self._journey_repository:
            journey = self._journey_repository.get_by_id(journey_id)
            if not journey:
                raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")

        return self._section_repository.get_by_journey_id(journey_id)

    def get_section(self, section_id: int) -> Section:
        """Retrieve a section by its ID."""
        section = self._section_repository.get_by_id(section_id)
        if not section:
            raise SectionNotFoundError(f"Section with ID {section_id} was not found.")
        return section

    def rename_section(self, section_id: int, title: str) -> Section:
        """Rename an existing section."""
        section = self.get_section(section_id)
        section.rename(title)
        return self._section_repository.update(section)

    def delete_section(self, section_id: int) -> None:
        """Delete a section and cascade delete its topics."""
        self.get_section(section_id)

        if self._topic_repository:
            self._topic_repository.delete_by_section_id(section_id)

        deleted = self._section_repository.delete(section_id)
        if not deleted:
            raise SectionNotFoundError(f"Section with ID {section_id} was not found.")
