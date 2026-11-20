"""SQLAlchemy database implementation of UserRepository."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.user_repository import UserRepository
from masar.domain.exceptions import UserAlreadyExistsError
from masar.domain.models import User
from masar.infrastructure.database.models import UserModel


class SqlUserRepository(UserRepository):
    """PostgreSQL/SQLAlchemy implementation for User persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def add(self, user: User) -> User:
        model = UserModel(
            email=user.email.strip().lower(),
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise UserAlreadyExistsError(f"User with email '{user.email}' already exists.") from exc
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.strip().lower())
        model = self._session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def get_all(self) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def delete(self, user_id: int) -> bool:
        model = self._session.get(UserModel, user_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
