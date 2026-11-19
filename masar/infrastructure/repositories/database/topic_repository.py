"""SQLAlchemy database implementation of TopicRepository."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import TopicNotFoundError
from masar.domain.models import Topic
from masar.infrastructure.database.models import TopicModel


class SqlTopicRepository(TopicRepository):
    """PostgreSQL/SQLAlchemy implementation for Topic persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: TopicModel) -> Topic:
        return Topic(
            id=model.id,
            section_id=model.section_id,
            title=model.title,
            is_completed=model.is_completed,
            created_at=model.created_at,
        )

    def add(self, topic: Topic) -> Topic:
        model = TopicModel(
            section_id=topic.section_id,
            title=topic.title,
            is_completed=topic.is_completed,
            created_at=topic.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, topic_id: int) -> Topic | None:
        model = self._session.get(TopicModel, topic_id)
        return self._to_entity(model) if model else None

    def get_by_section_id(self, section_id: int) -> list[Topic]:
        stmt = select(TopicModel).where(TopicModel.section_id == section_id).order_by(TopicModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def update(self, topic: Topic) -> Topic:
        if topic.id is None:
            raise ValueError("Cannot update topic without an ID")
        model = self._session.get(TopicModel, topic.id)
        if not model:
            raise TopicNotFoundError(f"Topic with ID {topic.id} was not found.")
        model.title = topic.title
        model.is_completed = topic.is_completed
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, topic_id: int) -> bool:
        model = self._session.get(TopicModel, topic_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def delete_by_section_id(self, section_id: int) -> int:
        stmt = delete(TopicModel).where(TopicModel.section_id == section_id)
        result = self._session.execute(stmt)
        self._session.commit()
        return int(result.rowcount)  # type: ignore[attr-defined]
