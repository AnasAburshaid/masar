"""In-memory note repository implementation."""

from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.domain.exceptions import NoteNotFoundError
from masar.domain.models import Note


class InMemoryNoteRepository(NoteRepository):
    """In-memory storage implementation for notes."""

    def __init__(self) -> None:
        self._notes: dict[int, Note] = {}
        self._next_id: int = 1

    def add(self, note: Note) -> Note:
        if note.id is None:
            note.id = self._next_id
            self._next_id += 1
        self._notes[note.id] = note
        return note

    def get_by_id(self, note_id: int) -> Note | None:
        return self._notes.get(note_id)

    def get_by_topic_id(self, topic_id: int) -> list[Note]:
        return [n for n in self._notes.values() if n.topic_id == topic_id]

    def update(self, note: Note) -> Note:
        if note.id is None or note.id not in self._notes:
            raise NoteNotFoundError(f"Note with ID {note.id} was not found.")
        self._notes[note.id] = note
        return note

    def delete(self, note_id: int) -> bool:
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False

    def delete_by_topic_id(self, topic_id: int) -> int:
        to_delete = [n_id for n_id, n in self._notes.items() if n.topic_id == topic_id]
        for n_id in to_delete:
            del self._notes[n_id]
        return len(to_delete)
