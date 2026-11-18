"""Note application service."""

from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import NoteNotFoundError, TopicNotFoundError
from masar.domain.models import Note


class NoteService:
    """Service handling notes attached to learning topics."""

    def __init__(
        self,
        note_repository: NoteRepository,
        topic_repository: TopicRepository | None = None,
    ) -> None:
        self._note_repository = note_repository
        self._topic_repository = topic_repository

    def create_note(self, topic_id: int, content: str) -> Note:
        """Add a new note to a topic."""
        if self._topic_repository:
            topic = self._topic_repository.get_by_id(topic_id)
            if not topic:
                raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")

        note = Note(topic_id=topic_id, content=content)
        return self._note_repository.add(note)

    def list_notes(self, topic_id: int) -> list[Note]:
        """List all notes belonging to a specific topic."""
        if self._topic_repository:
            topic = self._topic_repository.get_by_id(topic_id)
            if not topic:
                raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")

        return self._note_repository.get_by_topic_id(topic_id)

    def get_note(self, note_id: int) -> Note:
        """Retrieve a specific note by ID."""
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError(f"Note with ID {note_id} was not found.")
        return note

    def update_note(self, note_id: int, content: str) -> Note:
        """Update the content of an existing note."""
        note = self.get_note(note_id)
        note.update(content)
        return self._note_repository.update(note)

    def delete_note(self, note_id: int) -> None:
        """Delete a note by ID."""
        self.get_note(note_id)
        deleted = self._note_repository.delete(note_id)
        if not deleted:
            raise NoteNotFoundError(f"Note with ID {note_id} was not found.")
