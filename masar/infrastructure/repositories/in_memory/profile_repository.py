"""In-memory implementation of ProfileRepository for rapid testing."""

from typing import Optional

from masar.application.interfaces.repositories.profile_repository import (
    ProfileRepository,
)
from masar.domain.models.profile import LearningProfile, ProfileItem


class InMemoryProfileRepository(ProfileRepository):
    """In-memory storage implementation for learning profile items."""

    def __init__(self) -> None:
        self._items: dict[int, ProfileItem] = {}
        self._bios: dict[int, str] = {}
        self._next_id: int = 1

    def get_profile(self, user_id: int) -> LearningProfile:
        items = [i for i in self._items.values() if i.user_id == user_id]
        bio = self._bios.get(user_id, "")
        return LearningProfile(user_id=user_id, bio=bio, items=items)

    def add_item(self, item: ProfileItem) -> ProfileItem:
        if item.id is None:
            item.id = self._next_id
            self._next_id += 1
        self._items[item.id] = item
        return item

    def get_item(self, item_id: int) -> Optional[ProfileItem]:
        return self._items.get(item_id)

    def update_item(self, item: ProfileItem) -> ProfileItem:
        if item.id is None or item.id not in self._items:
            raise ValueError(f"Profile item {item.id} not found.")
        self._items[item.id] = item
        return item

    def delete_item(self, item_id: int) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def update_bio(self, user_id: int, bio: str) -> None:
        self._bios[user_id] = bio
