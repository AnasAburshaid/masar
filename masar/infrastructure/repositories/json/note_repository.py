"""JSON note repository implementation."""

from datetime import datetime, timezone
from pathlib import Path

from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.domain.exceptions import NoteNotFoundError
from masar.domain.models import Note
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonNoteRepository(NoteRepository):
    """JSON file persistence storage implementation for notes."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict) -> Note:
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

        updated_at = item.get("updated_at")
        if isinstance(updated_at, str):
            try:
                updated_dt = datetime.fromisoformat(updated_at)
            except ValueError:
                updated_dt = None
        elif isinstance(updated_at, datetime):
            updated_dt = updated_at
        else:
            updated_dt = None

        return Note(
            id=item["id"],
            topic_id=item["topic_id"],
            content=item["content"],
            created_at=created_dt,
            updated_at=updated_dt,
        )

    def _to_dict(self, note: Note) -> dict:
        return {
            "id": note.id,
            "topic_id": note.topic_id,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
        }

    def add(self, note: Note) -> Note:
        """Store note with an auto-incrementing ID."""
        data = self._storage.load()
        notes = data["notes"]

        if note.id is None:
            max_id = max((item["id"] for item in notes if "id" in item), default=0)
            note.id = max_id + 1

        notes.append(self._to_dict(note))
        self._storage.save(data)
        return note

    def get_by_id(self, note_id: int) -> Note | None:
        """Get note by ID."""
        data = self._storage.load()
        for item in data["notes"]:
            if item.get("id") == note_id:
                return self._to_entity(item)
        return None

    def get_by_topic_id(self, topic_id: int) -> list[Note]:
        """Get all notes belonging to a topic."""
        data = self._storage.load()
        return [
            self._to_entity(item)
            for item in data["notes"]
            if item.get("topic_id") == topic_id
        ]

    def update(self, note: Note) -> Note:
        """Update an existing note."""
        if note.id is None:
            raise NoteNotFoundError(f"Note with ID {note.id} was not found.")

        data = self._storage.load()
        found = False
        for i, item in enumerate(data["notes"]):
            if item.get("id") == note.id:
                data["notes"][i] = self._to_dict(note)
                found = True
                break

        if not found:
            raise NoteNotFoundError(f"Note with ID {note.id} was not found.")

        self._storage.save(data)
        return note

    def delete(self, note_id: int) -> bool:
        """Delete note by ID."""
        data = self._storage.load()
        initial_count = len(data["notes"])
        data["notes"] = [n for n in data["notes"] if n.get("id") != note_id]

        if len(data["notes"]) < initial_count:
            self._storage.save(data)
            return True
        return False

    def delete_by_topic_id(self, topic_id: int) -> int:
        """Delete all notes belonging to a topic."""
        data = self._storage.load()
        initial_count = len(data["notes"])
        data["notes"] = [n for n in data["notes"] if n.get("topic_id") != topic_id]
        deleted_count = initial_count - len(data["notes"])

        if deleted_count > 0:
            self._storage.save(data)
        return deleted_count
