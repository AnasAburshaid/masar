"""Journey repository abstraction."""

from abc import ABC, abstractmethod

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
