"""SQLAlchemy database implementation of NoteRepository."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.note_repository import NoteRepository
from masar.domain.exceptions import NoteNotFoundError
from masar.domain.models import Note
from masar.infrastructure.database.models import NoteModel


class SqlNoteRepository(NoteRepository):
    """PostgreSQL/SQLAlchemy implementation for Note persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: NoteModel) -> Note:
        return Note(
            id=model.id,
            topic_id=model.topic_id,
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def add(self, note: Note) -> Note:
        model = NoteModel(
            topic_id=note.topic_id,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, note_id: int) -> Note | None:
        model = self._session.get(NoteModel, note_id)
        return self._to_entity(model) if model else None

    def get_by_topic_id(self, topic_id: int) -> list[Note]:
        stmt = select(NoteModel).where(NoteModel.topic_id == topic_id).order_by(NoteModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def update(self, note: Note) -> Note:
        if note.id is None:
            raise ValueError("Cannot update note without an ID")
        model = self._session.get(NoteModel, note.id)
        if not model:
            raise NoteNotFoundError(f"Note with ID {note.id} was not found.")
        model.content = note.content
        model.updated_at = note.updated_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, note_id: int) -> bool:
        model = self._session.get(NoteModel, note_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def delete_by_topic_id(self, topic_id: int) -> int:
        stmt = delete(NoteModel).where(NoteModel.topic_id == topic_id)
        result = self._session.execute(stmt)
        self._session.commit()
        return int(result.rowcount)  # type: ignore[attr-defined]
