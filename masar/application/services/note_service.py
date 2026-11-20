"""Note application service."""

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import (
    AccessDeniedError,
    NoteNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Note


class NoteService:
    """Service handling notes attached to learning topics."""

    def __init__(
        self,
        note_repository: NoteRepository,
        topic_repository: TopicRepository | None = None,
        section_repository: SectionRepository | None = None,
        journey_repository: JourneyRepository | None = None,
    ) -> None:
        self._note_repository = note_repository
        self._topic_repository = topic_repository
        self._section_repository = section_repository
        self._journey_repository = journey_repository

    def _verify_topic_ownership(self, topic_id: int, user_id: int | None) -> None:
        if self._topic_repository:
            topic = self._topic_repository.get_by_id(topic_id)
            if not topic:
                raise TopicNotFoundError(f"Topic with ID {topic_id} was not found.")
            if user_id is not None and self._section_repository and self._journey_repository:
                section = self._section_repository.get_by_id(topic.section_id)
                if not section:
                    raise SectionNotFoundError(f"Section with ID {topic.section_id} was not found.")
                journey = self._journey_repository.get_by_id(section.journey_id)
                if journey and journey.user_id is not None and journey.user_id != user_id:
                    raise AccessDeniedError("You do not have permission to access notes for this topic.")

    def create_note(
        self,
        topic_id: int,
        content: str,
        user_id: int | None = None,
    ) -> Note:
        """Add a new note to a topic."""
        self._verify_topic_ownership(topic_id, user_id)
        note = Note(topic_id=topic_id, content=content)
        return self._note_repository.add(note)

    def list_notes(
        self,
        topic_id: int,
        user_id: int | None = None,
    ) -> list[Note]:
        """List all notes belonging to a specific topic."""
        self._verify_topic_ownership(topic_id, user_id)
        return self._note_repository.get_by_topic_id(topic_id)

    def get_note(
        self,
        note_id: int,
        user_id: int | None = None,
    ) -> Note:
        """Retrieve a specific note by ID."""
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError(f"Note with ID {note_id} was not found.")
        self._verify_topic_ownership(note.topic_id, user_id)
        return note

    def update_note(
        self,
        note_id: int,
        content: str,
        user_id: int | None = None,
    ) -> Note:
        """Update the content of an existing note."""
        note = self.get_note(note_id, user_id=user_id)
        note.update(content)
        return self._note_repository.update(note)

    def delete_note(
        self,
        note_id: int,
        user_id: int | None = None,
    ) -> None:
        """Delete a note by ID."""
        self.get_note(note_id, user_id=user_id)
        deleted = self._note_repository.delete(note_id)
        if not deleted:
            raise NoteNotFoundError(f"Note with ID {note_id} was not found.")
