"""Application services coordinating use cases."""

from masar.domain.exceptions import (
    JourneyNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Journey, Section, Topic
from masar.infrastructure.repositories import (
    InMemoryJourneyRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
    JourneyRepository,
    SectionRepository,
    TopicRepository,
)


class JourneyService:
    """Service handling learning journey use cases."""

    def __init__(
        self,
        repository: JourneyRepository | None = None,
        section_repository: SectionRepository | None = None,
        topic_repository: TopicRepository | None = None,
    ) -> None:
        self._repository = repository or InMemoryJourneyRepository()
        self._section_repository = section_repository
        self._topic_repository = topic_repository

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
        """Delete a journey by ID and cascade delete associated sections/topics."""
        journey = self.get_journey(journey_id)

        # Cascade delete sections and topics if repositories are attached
        if self._section_repository:
            sections = self._section_repository.get_by_journey_id(journey_id)
            for section in sections:
                if self._topic_repository and section.id is not None:
                    self._topic_repository.delete_by_section_id(section.id)
                if section.id is not None:
                    self._section_repository.delete(section.id)

        deleted = self._repository.delete(journey_id)
        if not deleted:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")


class SectionService:
    """Service handling sections within learning journeys."""

    def __init__(
        self,
        section_repository: SectionRepository | None = None,
        journey_repository: JourneyRepository | None = None,
        topic_repository: TopicRepository | None = None,
    ) -> None:
        self._section_repository = section_repository or InMemorySectionRepository()
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


class TopicService:
    """Service handling topics within sections."""

    def __init__(
        self,
        topic_repository: TopicRepository | None = None,
        section_repository: SectionRepository | None = None,
    ) -> None:
        self._topic_repository = topic_repository or InMemoryTopicRepository()
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
