"""JSON topic repository implementation."""

from pathlib import Path
from typing import Any

from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import TopicNotFoundError
from masar.domain.models import Topic
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonTopicRepository(TopicRepository):
    """JSON file persistence storage implementation for topics."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict[str, Any]) -> Topic:
        return Topic(
            id=item["id"],
            section_id=item["section_id"],
            title=item["title"],
            is_completed=item.get("is_completed", False),
        )

    def _to_dict(self, topic: Topic) -> dict[str, Any]:
        return {
            "id": topic.id,
            "section_id": topic.section_id,
            "title": topic.title,
            "is_completed": topic.is_completed,
        }

    def add(self, topic: Topic) -> Topic:
        """Store topic with an auto-incrementing ID."""
        data = self._storage.load()
        topics = data["topics"]

        if topic.id is None:
            max_id = max((item["id"] for item in topics if "id" in item), default=0)
            topic.id = max_id + 1

        topics.append(self._to_dict(topic))
        self._storage.save(data)
        return topic

    def get_by_id(self, topic_id: int) -> Topic | None:
        """Get topic by ID."""
        data = self._storage.load()
        for item in data["topics"]:
            if item.get("id") == topic_id:
                return self._to_entity(item)
        return None

    def get_by_section_id(self, section_id: int) -> list[Topic]:
        """Get all topics belonging to a section."""
        data = self._storage.load()
        return [
            self._to_entity(item)
            for item in data["topics"]
            if item.get("section_id") == section_id
        ]

    def update(self, topic: Topic) -> Topic:
        """Update an existing topic."""
        if topic.id is None:
            raise TopicNotFoundError(f"Topic with ID {topic.id} was not found.")

        data = self._storage.load()
        found = False
        for i, item in enumerate(data["topics"]):
            if item.get("id") == topic.id:
                data["topics"][i] = self._to_dict(topic)
                found = True
                break

        if not found:
            raise TopicNotFoundError(f"Topic with ID {topic.id} was not found.")

        self._storage.save(data)
        return topic

    def delete(self, topic_id: int) -> bool:
        """Delete topic by ID."""
        data = self._storage.load()
        initial_count = len(data["topics"])
        data["topics"] = [t for t in data["topics"] if t.get("id") != topic_id]

        if len(data["topics"]) < initial_count:
            self._storage.save(data)
            return True
        return False

    def delete_by_section_id(self, section_id: int) -> int:
        """Delete all topics belonging to a section."""
        data = self._storage.load()
        initial_count = len(data["topics"])
        data["topics"] = [t for t in data["topics"] if t.get("section_id") != section_id]
        deleted_count = initial_count - len(data["topics"])

        if deleted_count > 0:
            self._storage.save(data)
        return deleted_count
