"""JSON journey repository implementation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonJourneyRepository(JourneyRepository):
    """JSON file persistence storage implementation for learning journeys."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict[str, Any]) -> Journey:
        created_at = item.get("created_at")
        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                created_dt = datetime.now(timezone.utc)
        elif isinstance(created_at, datetime):
            created_dt = created_at
        else:
            created_dt = datetime.now(timezone.utc)

        return Journey(
            id=item["id"],
            user_id=item.get("user_id"),
            title=item["title"],
            description=item.get("description") or "",
            created_at=created_dt,
        )

    def _to_dict(self, journey: Journey) -> dict[str, Any]:
        return {
            "id": journey.id,
            "user_id": journey.user_id,
            "title": journey.title,
            "description": journey.description,
            "created_at": journey.created_at.isoformat() if journey.created_at else None,
        }

    def add(self, journey: Journey) -> Journey:
        """Store journey with an auto-incrementing ID."""
        data = self._storage.load()
        journeys = data["journeys"]

        if journey.id is None:
            max_id = max((item["id"] for item in journeys if "id" in item), default=0)
            journey.id = max_id + 1

        journeys.append(self._to_dict(journey))
        self._storage.save(data)
        return journey

    def get_by_id(self, journey_id: int) -> Journey | None:
        """Get journey by ID."""
        data = self._storage.load()
        for item in data["journeys"]:
            if item.get("id") == journey_id:
                return self._to_entity(item)
        return None

    def get_all(self) -> list[Journey]:
        """Get all journeys ordered by ID."""
        data = self._storage.load()
        return [self._to_entity(item) for item in data["journeys"]]

    def get_by_user_id(self, user_id: int) -> list[Journey]:
        """Get all journeys belonging to a specific user ordered by ID."""
        return [j for j in self.get_all() if j.user_id == user_id]

    def update(self, journey: Journey) -> Journey:
        """Update an existing journey."""
        if journey.id is None:
            raise JourneyNotFoundError(f"Journey with ID {journey.id} was not found.")

        data = self._storage.load()
        found = False
        for i, item in enumerate(data["journeys"]):
            if item.get("id") == journey.id:
                data["journeys"][i] = self._to_dict(journey)
                found = True
                break

        if not found:
            raise JourneyNotFoundError(f"Journey with ID {journey.id} was not found.")

        self._storage.save(data)
        return journey

    def delete(self, journey_id: int) -> bool:
        """Delete journey by ID."""
        data = self._storage.load()
        initial_count = len(data["journeys"])
        data["journeys"] = [j for j in data["journeys"] if j.get("id") != journey_id]

        if len(data["journeys"]) < initial_count:
            self._storage.save(data)
            return True
        return False
