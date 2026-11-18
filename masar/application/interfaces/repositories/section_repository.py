"""Section repository abstraction."""

from abc import ABC, abstractmethod

from masar.domain.models import Section


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
