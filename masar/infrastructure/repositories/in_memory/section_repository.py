"""In-memory section repository implementation."""

from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.domain.exceptions import SectionNotFoundError
from masar.domain.models import Section


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
