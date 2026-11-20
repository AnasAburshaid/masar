"""User application service for registration, authentication, and account management."""

from masar.application.interfaces.repositories.user_repository import UserRepository
from masar.application.interfaces.security.password_hasher import PasswordHasher
from masar.application.interfaces.security.token_service import TokenService
from masar.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from masar.domain.models import User


class UserService:
    """Coordinates user registration, credentials verification, and token authentication."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService | None = None,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service

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

    def login_user(self, email: str, password: str) -> tuple[User, str]:
        """Verify credentials and issue a signed JWT access token."""
        user = self.authenticate_user(email, password)
        if not user or user.id is None:
            raise InvalidCredentialsError("Invalid email or password.")
        if self.token_service is None:
            raise RuntimeError("Token service is not configured.")
        access_token = self.token_service.create_access_token(
            subject=user.id,
            claims={"email": user.email},
        )
        return user, access_token

    def get_user_from_token(self, token: str) -> User:
        """Validate token and return authenticated active user entity."""
        if self.token_service is None:
            raise RuntimeError("Token service is not configured.")
        payload = self.token_service.decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise InvalidTokenError("Token payload missing subject.")
        try:
            user_id = int(sub)
        except (ValueError, TypeError) as exc:
            raise InvalidTokenError("Invalid subject identifier in token.") from exc

        try:
            user = self.get_user_by_id(user_id)
        except UserNotFoundError as exc:
            raise InvalidTokenError("User belonging to this token no longer exists.") from exc

        if not user.is_active:
            raise InvalidTokenError("User account is inactive.")
        return user
