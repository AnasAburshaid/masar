"""JSON profile repository implementation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from masar.application.interfaces.repositories.profile_repository import (
    ProfileRepository,
)
from masar.domain.models.profile import LearningProfile, ProfileItem
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonProfileRepository(ProfileRepository):
    """JSON file persistence storage implementation for LearningProfile items."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict[str, Any]) -> ProfileItem:
        created_at = item.get("created_at")
        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                created_dt = datetime.now(timezone.utc)
        else:
            created_dt = datetime.now(timezone.utc)

        updated_at = item.get("updated_at")
        if isinstance(updated_at, str):
            try:
                updated_dt = datetime.fromisoformat(updated_at)
            except ValueError:
                updated_dt = None
        else:
            updated_dt = None

        return ProfileItem(
            id=item["id"],
            user_id=item["user_id"],
            category=item["category"],
            name=item["name"],
            level=item.get("level"),
            is_confirmed=item.get("is_confirmed", False),
            source_type=item.get("source_type", "manual"),
            source_id=item.get("source_id"),
            created_at=created_dt,
            updated_at=updated_dt,
        )

    def _to_dict(self, item: ProfileItem) -> dict[str, Any]:
        return {
            "id": item.id,
            "user_id": item.user_id,
            "category": item.category,
            "name": item.name,
            "level": item.level,
            "is_confirmed": item.is_confirmed,
            "source_type": item.source_type,
            "source_id": item.source_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    def get_profile(self, user_id: int) -> LearningProfile:
        data = self._storage.load()
        items_data = data.get("profile_items", [])
        items = [self._to_entity(i) for i in items_data if i.get("user_id") == user_id]

        users_data = data.get("users", [])
        bio = ""
        for u in users_data:
            if u.get("id") == user_id:
                bio = u.get("bio", "")
                break

        return LearningProfile(user_id=user_id, bio=bio, items=items)

    def add_item(self, item: ProfileItem) -> ProfileItem:
        data = self._storage.load()
        items = data.get("profile_items", [])
        if item.id is None:
            max_id = max((i["id"] for i in items), default=0)
            item.id = max_id + 1
        items.append(self._to_dict(item))
        data["profile_items"] = items
        self._storage.save(data)
        return item

    def get_item(self, item_id: int) -> Optional[ProfileItem]:
        data = self._storage.load()
        items = data.get("profile_items", [])
        for item in items:
            if item.get("id") == item_id:
                return self._to_entity(item)
        return None

    def update_item(self, item: ProfileItem) -> ProfileItem:
        if item.id is None:
            raise ValueError("Cannot update a profile item without an ID.")
        data = self._storage.load()
        items = data.get("profile_items", [])
        for i, val in enumerate(items):
            if val.get("id") == item.id:
                items[i] = self._to_dict(item)
                data["profile_items"] = items
                self._storage.save(data)
                return item
        raise ValueError(f"Profile item {item.id} not found.")

    def delete_item(self, item_id: int) -> bool:
        data = self._storage.load()
        items = data.get("profile_items", [])
        filtered = [i for i in items if i.get("id") != item_id]
        if len(filtered) < len(items):
            data["profile_items"] = filtered
            self._storage.save(data)
            return True
        return False

    def update_bio(self, user_id: int, bio: str) -> None:
        data = self._storage.load()
        users = data.get("users", [])
        for u in users:
            if u.get("id") == user_id:
                u["bio"] = bio
                break
        data["users"] = users
        self._storage.save(data)
