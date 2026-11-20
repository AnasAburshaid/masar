"""Profile repository abstraction interface."""

from abc import ABC, abstractmethod
from typing import Optional

from masar.domain.models.profile import LearningProfile, ProfileItem


class ProfileRepository(ABC):
    """Abstract interface defining persistence operations for user knowledge profiles."""

    @abstractmethod
    def get_profile(self, user_id: int) -> LearningProfile:
        """Retrieve complete learning profile for a user."""
        raise NotImplementedError

    @abstractmethod
    def add_item(self, item: ProfileItem) -> ProfileItem:
        """Persist a new profile item and return it with an allocated ID."""
        raise NotImplementedError

    @abstractmethod
    def get_item(self, item_id: int) -> Optional[ProfileItem]:
        """Retrieve a specific profile item by unique ID or return None."""
        raise NotImplementedError

    @abstractmethod
    def update_item(self, item: ProfileItem) -> ProfileItem:
        """Update an existing profile item."""
        raise NotImplementedError

    @abstractmethod
    def delete_item(self, item_id: int) -> bool:
        """Delete a profile item by unique ID. Returns True if deleted, False otherwise."""
        raise NotImplementedError

    @abstractmethod
    def update_bio(self, user_id: int, bio: str) -> None:
        """Update the user's high-level professional/learning bio summary."""
        raise NotImplementedError
