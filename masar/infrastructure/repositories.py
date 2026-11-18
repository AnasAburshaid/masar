"""Repository implementations for data persistence."""

from abc import ABC, abstractmethod

from masar.domain.exceptions import (
    JourneyNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Journey, Section, Topic


class JourneyRepository(ABC):
    """Abstract repository interface for Learning Journeys."""

    @abstractmethod
    def add(self, journey: Journey) -> Journey:
        """Add a new journey to storage."""

    @abstractmethod
    def get_by_id(self, journey_id: int) -> Journey | None:
        """Retrieve a journey by its unique identifier."""

    @abstractmethod
    def get_all(self) -> list[Journey]:
        """Retrieve all journeys."""

    @abstractmethod
    def update(self, journey: Journey) -> Journey:
        """Update an existing journey."""

    @abstractmethod
    def delete(self, journey_id: int) -> bool:
        """Delete a journey by ID. Returns True if deleted, False otherwise."""


class InMemoryJourneyRepository(JourneyRepository):
    """In-memory storage implementation for learning journeys."""

    def __init__(self) -> None:
        self._journeys: dict[int, Journey] = {}
        self._next_id: int = 1

    def add(self, journey: Journey) -> Journey:
        """Store journey with an auto-incrementing ID."""
        if journey.id is None:
            journey.id = self._next_id
            self._next_id += 1
        self._journeys[journey.id] = journey
        return journey

    def get_by_id(self, journey_id: int) -> Journey | None:
        """Get journey by ID."""
        return self._journeys.get(journey_id)

    def get_all(self) -> list[Journey]:
        """Get all journeys ordered by ID."""
        return list(self._journeys.values())

    def update(self, journey: Journey) -> Journey:
        """Update an existing journey."""
        if journey.id is None or journey.id not in self._journeys:
            raise JourneyNotFoundError(f"Journey with ID {journey.id} was not found.")
        self._journeys[journey.id] = journey
        return journey

    def delete(self, journey_id: int) -> bool:
        """Delete journey by ID."""
        if journey_id in self._journeys:
            del self._journeys[journey_id]
            return True
        return False


class SectionRepository(ABC):
    """Abstract repository interface for Sections."""

    @abstractmethod
    def add(self, section: Section) -> Section:
        """Add a new section to storage."""

    @abstractmethod
    def get_by_id(self, section_id: int) -> Section | None:
        """Retrieve a section by its ID."""

    @abstractmethod
    def get_by_journey_id(self, journey_id: int) -> list[Section]:
        """Retrieve all sections belonging to a journey."""

    @abstractmethod
    def update(self, section: Section) -> Section:
        """Update an existing section."""

    @abstractmethod
    def delete(self, section_id: int) -> bool:
        """Delete a section by ID."""

    @abstractmethod
    def delete_by_journey_id(self, journey_id: int) -> int:
        """Delete all sections belonging to a journey."""


class InMemorySectionRepository(SectionRepository):
    """In-memory storage implementation for sections."""

    def __init__(self) -> None:
        self._sections: dict[int, Section] = {}
        self._next_id: int = 1

    def add(self, section: Section) -> Section:
        if section.id is None:
            section.id = self._next_id
            self._next_id += 1
        self._sections[section.id] = section
        return section

    def get_by_id(self, section_id: int) -> Section | None:
        return self._sections.get(section_id)

    def get_by_journey_id(self, journey_id: int) -> list[Section]:
        return [s for s in self._sections.values() if s.journey_id == journey_id]

    def update(self, section: Section) -> Section:
        if section.id is None or section.id not in self._sections:
            raise SectionNotFoundError(f"Section with ID {section.id} was not found.")
        self._sections[section.id] = section
        return section

    def delete(self, section_id: int) -> bool:
        if section_id in self._sections:
            del self._sections[section_id]
            return True
        return False

    def delete_by_journey_id(self, journey_id: int) -> int:
        to_delete = [s_id for s_id, s in self._sections.items() if s.journey_id == journey_id]
        for s_id in to_delete:
            del self._sections[s_id]
        return len(to_delete)


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


class InMemoryTopicRepository(TopicRepository):
    """In-memory storage implementation for topics."""

    def __init__(self) -> None:
        self._topics: dict[int, Topic] = {}
        self._next_id: int = 1

    def add(self, topic: Topic) -> Topic:
        if topic.id is None:
            topic.id = self._next_id
            self._next_id += 1
        self._topics[topic.id] = topic
        return topic

    def get_by_id(self, topic_id: int) -> Topic | None:
        return self._topics.get(topic_id)

    def get_by_section_id(self, section_id: int) -> list[Topic]:
        return [t for t in self._topics.values() if t.section_id == section_id]

    def update(self, topic: Topic) -> Topic:
        if topic.id is None or topic.id not in self._topics:
            raise TopicNotFoundError(f"Topic with ID {topic.id} was not found.")
        self._topics[topic.id] = topic
        return topic

    def delete(self, topic_id: int) -> bool:
        if topic_id in self._topics:
            del self._topics[topic_id]
            return True
        return False

    def delete_by_section_id(self, section_id: int) -> int:
        to_delete = [t_id for t_id, t in self._topics.items() if t.section_id == section_id]
        for t_id in to_delete:
            del self._topics[t_id]
        return len(to_delete)
