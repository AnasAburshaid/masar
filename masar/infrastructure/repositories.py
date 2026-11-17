"""Repository implementations for data persistence."""

from abc import ABC, abstractmethod

from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey


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
