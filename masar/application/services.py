"""Application services coordinating use cases."""

from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey
from masar.infrastructure.repositories import (
    InMemoryJourneyRepository,
    JourneyRepository,
)


class JourneyService:
    """Service handling learning journey use cases."""

    def __init__(self, repository: JourneyRepository | None = None) -> None:
        self._repository = repository or InMemoryJourneyRepository()

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
        """Delete a journey by ID."""
        deleted = self._repository.delete(journey_id)
        if not deleted:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} was not found.")
