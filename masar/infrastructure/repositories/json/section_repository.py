"""JSON section repository implementation."""

from pathlib import Path

from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.domain.exceptions import SectionNotFoundError
from masar.domain.models import Section
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonSectionRepository(SectionRepository):
    """JSON file persistence storage implementation for sections."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict) -> Section:
        return Section(
            id=item["id"],
            journey_id=item["journey_id"],
            title=item["title"],
        )

    def _to_dict(self, section: Section) -> dict:
        return {
            "id": section.id,
            "journey_id": section.journey_id,
            "title": section.title,
        }

    def add(self, section: Section) -> Section:
        """Store section with an auto-incrementing ID."""
        data = self._storage.load()
        sections = data["sections"]

        if section.id is None:
            max_id = max((item["id"] for item in sections if "id" in item), default=0)
            section.id = max_id + 1

        sections.append(self._to_dict(section))
        self._storage.save(data)
        return section

    def get_by_id(self, section_id: int) -> Section | None:
        """Get section by ID."""
        data = self._storage.load()
        for item in data["sections"]:
            if item.get("id") == section_id:
                return self._to_entity(item)
        return None

    def get_by_journey_id(self, journey_id: int) -> list[Section]:
        """Get all sections belonging to a journey."""
        data = self._storage.load()
        return [
            self._to_entity(item)
            for item in data["sections"]
            if item.get("journey_id") == journey_id
        ]

    def update(self, section: Section) -> Section:
        """Update an existing section."""
        if section.id is None:
            raise SectionNotFoundError(f"Section with ID {section.id} was not found.")

        data = self._storage.load()
        found = False
        for i, item in enumerate(data["sections"]):
            if item.get("id") == section.id:
                data["sections"][i] = self._to_dict(section)
                found = True
                break

        if not found:
            raise SectionNotFoundError(f"Section with ID {section.id} was not found.")

        self._storage.save(data)
        return section

    def delete(self, section_id: int) -> bool:
        """Delete section by ID."""
        data = self._storage.load()
        initial_count = len(data["sections"])
        data["sections"] = [s for s in data["sections"] if s.get("id") != section_id]

        if len(data["sections"]) < initial_count:
            self._storage.save(data)
            return True
        return False

    def delete_by_journey_id(self, journey_id: int) -> int:
        """Delete all sections belonging to a journey."""
        data = self._storage.load()
        initial_count = len(data["sections"])
        data["sections"] = [s for s in data["sections"] if s.get("journey_id") != journey_id]
        deleted_count = initial_count - len(data["sections"])

        if deleted_count > 0:
            self._storage.save(data)
        return deleted_count
