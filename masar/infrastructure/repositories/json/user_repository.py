"""JSON user repository implementation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from masar.application.interfaces.repositories.user_repository import (
    UserRepository,
)
from masar.domain.exceptions import UserAlreadyExistsError
from masar.domain.models import User
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonUserRepository(UserRepository):
    """JSON file persistence storage implementation for Users."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict[str, Any]) -> User:
        created_at = item.get("created_at")
        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                created_dt = datetime.now(timezone.utc)
        elif isinstance(created_at, datetime):
            created_dt = created_at
        else:
            created_dt = datetime.now(timezone.utc)

        return User(
            id=item["id"],
            email=item["email"],
            hashed_password=item["hashed_password"],
            is_active=item.get("is_active", True),
            created_at=created_dt,
        )

    def _to_dict(self, user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def add(self, user: User) -> User:
        """Store user with an auto-incrementing ID."""
        data = self._storage.load()
        users = data.get("users", [])

        normalized_email = user.email.strip().lower()
        if any(item.get("email", "").strip().lower() == normalized_email for item in users):
            raise UserAlreadyExistsError(f"User with email '{user.email}' already exists.")

        if user.id is None:
            max_id = max((item["id"] for item in users if "id" in item), default=0)
            user.id = max_id + 1

        users.append(self._to_dict(user))
        data["users"] = users
        self._storage.save(data)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        data = self._storage.load()
        for item in data.get("users", []):
            if item.get("id") == user_id:
                return self._to_entity(item)
        return None

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address (case-insensitive)."""
        data = self._storage.load()
        normalized = email.strip().lower()
        for item in data.get("users", []):
            if item.get("email", "").strip().lower() == normalized:
                return self._to_entity(item)
        return None

    def get_all(self) -> list[User]:
        """Get all users ordered by ID."""
        data = self._storage.load()
        return [self._to_entity(item) for item in data.get("users", [])]

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        data = self._storage.load()
        users = data.get("users", [])
        original_length = len(users)
        data["users"] = [item for item in users if item.get("id") != user_id]

        if len(data["users"]) < original_length:
            self._storage.save(data)
            return True
        return False
