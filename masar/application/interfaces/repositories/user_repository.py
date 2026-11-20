"""User repository abstraction."""

from abc import ABC, abstractmethod

from masar.domain.models import User


class UserRepository(ABC):
    """Abstract repository interface for User persistence."""

    @abstractmethod
    def add(self, user: User) -> User:
        """Persist a new user."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by ID."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email address."""

    @abstractmethod
    def get_all(self) -> list[User]:
        """Retrieve all users."""

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
