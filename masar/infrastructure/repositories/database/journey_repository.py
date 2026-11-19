"""SQLAlchemy database implementation of JourneyRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.journey_repository import (
    JourneyRepository,
)
from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey
from masar.infrastructure.database.models import JourneyModel


class SqlJourneyRepository(JourneyRepository):
    """PostgreSQL/SQLAlchemy implementation for Journey persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: JourneyModel) -> Journey:
        return Journey(
            id=model.id,
            title=model.title,
            description=model.description,
            created_at=model.created_at,
        )

    def add(self, entity: Journey) -> Journey:
        model = JourneyModel(
            title=entity.title,
            description=entity.description,
            created_at=entity.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, entity_id: int) -> Journey | None:
        model = self._session.get(JourneyModel, entity_id)
        return self._to_entity(model) if model else None

    def get_all(self) -> list[Journey]:
        stmt = select(JourneyModel).order_by(JourneyModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def update(self, entity: Journey) -> Journey:
        if entity.id is None:
            raise ValueError("Cannot update entity without an ID")
        model = self._session.get(JourneyModel, entity.id)
        if not model:
            raise JourneyNotFoundError(f"Journey with ID {entity.id} was not found.")
        model.title = entity.title
        model.description = entity.description
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, entity_id: int) -> bool:
        model = self._session.get(JourneyModel, entity_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
