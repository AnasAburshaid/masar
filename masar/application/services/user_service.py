"""User application service for registration and account management."""

from masar.application.interfaces.repositories.user_repository import UserRepository
from masar.application.interfaces.security.password_hasher import PasswordHasher
from masar.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from masar.domain.models import User


class UserService:
    """Coordinates user registration, validation, and retrieval."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def register_user(self, email: str, password: str) -> User:
        """Register a new user with hashed password after validation."""
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        normalized_email = email.strip().lower()
        existing = self.user_repository.get_by_email(normalized_email)
        if existing:
            raise UserAlreadyExistsError(f"User with email '{normalized_email}' already exists.")

        hashed = self.password_hasher.hash(password)
        user = User(
            email=normalized_email,
            hashed_password=hashed,
        )
        return self.user_repository.add(user)

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieve a user by ID or raise UserNotFoundError."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} was not found.")
        return user

    def get_user_by_email(self, email: str) -> User:
        """Retrieve a user by email or raise UserNotFoundError."""
        user = self.user_repository.get_by_email(email.strip().lower())
        if not user:
            raise UserNotFoundError(f"User with email '{email}' was not found.")
        return user

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Verify user credentials and return the user if valid."""
        user = self.user_repository.get_by_email(email.strip().lower())
        if not user or not user.is_active:
            return None
        if self.password_hasher.verify(password, user.hashed_password):
            return user
        return None
