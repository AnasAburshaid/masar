"""SQLAlchemy implementation of ProfileRepository."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.profile_repository import (
    ProfileRepository,
)
from masar.domain.models.profile import LearningProfile, ProfileItem
from masar.infrastructure.database.models import ProfileItemModel, UserModel


class SqlProfileRepository(ProfileRepository):
    """SQLAlchemy repository for learning knowledge profile items and bio."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: ProfileItemModel) -> ProfileItem:
        return ProfileItem(
            id=model.id,
            user_id=model.user_id,
            category=model.category,
            name=model.name,
            level=model.level,
            is_confirmed=model.is_confirmed,
            source_type=model.source_type,
            source_id=model.source_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_profile(self, user_id: int) -> LearningProfile:
        user = self._session.get(UserModel, user_id)
        bio = user.bio if user and hasattr(user, "bio") else ""

        stmt = (
            select(ProfileItemModel)
            .where(ProfileItemModel.user_id == user_id)
            .order_by(ProfileItemModel.category, ProfileItemModel.name)
        )
        models = self._session.scalars(stmt).all()
        items = [self._to_entity(m) for m in models]
        return LearningProfile(user_id=user_id, bio=bio, items=items)

    def add_item(self, item: ProfileItem) -> ProfileItem:
        model = ProfileItemModel(
            user_id=item.user_id,
            category=item.category,
            name=item.name,
            level=item.level,
            is_confirmed=item.is_confirmed,
            source_type=item.source_type,
            source_id=item.source_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_item(self, item_id: int) -> Optional[ProfileItem]:
        model = self._session.get(ProfileItemModel, item_id)
        return self._to_entity(model) if model else None

    def update_item(self, item: ProfileItem) -> ProfileItem:
        if item.id is None:
            raise ValueError("Cannot update a profile item without an ID.")
        model = self._session.get(ProfileItemModel, item.id)
        if model is None:
            raise ValueError(f"Profile item {item.id} not found.")
        model.category = item.category
        model.name = item.name
        model.level = item.level
        model.is_confirmed = item.is_confirmed
        model.source_type = item.source_type
        model.source_id = item.source_id
        model.updated_at = item.updated_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete_item(self, item_id: int) -> bool:
        model = self._session.get(ProfileItemModel, item_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def update_bio(self, user_id: int, bio: str) -> None:
        user = self._session.get(UserModel, user_id)
        if user is not None:
            user.bio = bio
            self._session.commit()
