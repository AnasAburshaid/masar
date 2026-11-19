"""SQLAlchemy database implementation of SectionRepository."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.section_repository import (
    SectionRepository,
)
from masar.domain.exceptions import SectionNotFoundError
from masar.domain.models import Section
from masar.infrastructure.database.models import SectionModel


class SqlSectionRepository(SectionRepository):
    """PostgreSQL/SQLAlchemy implementation for Section persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: SectionModel) -> Section:
        return Section(
            id=model.id,
            journey_id=model.journey_id,
            title=model.title,
            created_at=model.created_at,
        )

    def add(self, section: Section) -> Section:
        model = SectionModel(
            journey_id=section.journey_id,
            title=section.title,
            created_at=section.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, section_id: int) -> Section | None:
        model = self._session.get(SectionModel, section_id)
        return self._to_entity(model) if model else None

    def get_by_journey_id(self, journey_id: int) -> list[Section]:
        stmt = select(SectionModel).where(SectionModel.journey_id == journey_id).order_by(SectionModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def update(self, section: Section) -> Section:
        if section.id is None:
            raise ValueError("Cannot update section without an ID")
        model = self._session.get(SectionModel, section.id)
        if not model:
            raise SectionNotFoundError(f"Section with ID {section.id} was not found.")
        model.title = section.title
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, section_id: int) -> bool:
        model = self._session.get(SectionModel, section_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def delete_by_journey_id(self, journey_id: int) -> int:
        stmt = delete(SectionModel).where(SectionModel.journey_id == journey_id)
        result = self._session.execute(stmt)
        self._session.commit()
        return int(result.rowcount)  # type: ignore[attr-defined]
