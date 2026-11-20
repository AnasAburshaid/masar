"""In-memory journey repository implementation."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey


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

    def get_by_user_id(self, user_id: int) -> list[Journey]:
        """Get all journeys belonging to a specific user ordered by ID."""
        return [j for j in self._journeys.values() if j.user_id == user_id]

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
