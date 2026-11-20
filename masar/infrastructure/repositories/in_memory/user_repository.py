"""In-memory user repository implementation."""

from masar.application.interfaces.repositories.user_repository import UserRepository
from masar.domain.exceptions import UserAlreadyExistsError
from masar.domain.models import User


class InMemoryUserRepository(UserRepository):
    """In-memory storage implementation for User persistence."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id: int = 1

    def add(self, user: User) -> User:
        """Store user with an auto-incrementing ID."""
        normalized_email = user.email.strip().lower()
        if any(u.email == normalized_email for u in self._users.values()):
            raise UserAlreadyExistsError(f"User with email '{user.email}' already exists.")

        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        normalized = email.strip().lower()
        for u in self._users.values():
            if u.email == normalized:
                return u
        return None

    def get_all(self) -> list[User]:
        """Get all users ordered by ID."""
        return list(self._users.values())

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
