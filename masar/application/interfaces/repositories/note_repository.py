"""Note repository abstraction."""

from abc import ABC, abstractmethod

from masar.domain.models import Note


class NoteRepository(ABC):
    """Abstract repository interface for Notes."""

    @abstractmethod
    def add(self, note: Note) -> Note:
        """Add a new note to storage."""

    @abstractmethod
    def get_by_id(self, note_id: int) -> Note | None:
        """Retrieve a note by its ID."""

    @abstractmethod
    def get_by_topic_id(self, topic_id: int) -> list[Note]:
        """Retrieve all notes belonging to a topic."""

    @abstractmethod
    def update(self, note: Note) -> Note:
        """Update an existing note."""

    @abstractmethod
    def delete(self, note_id: int) -> bool:
        """Delete a note by ID."""

    @abstractmethod
    def delete_by_topic_id(self, topic_id: int) -> int:
        """Delete all notes belonging to a topic."""
