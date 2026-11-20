"""Password hasher abstraction."""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Abstract interface for hashing and verifying passwords."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Hash a plaintext password securely."""

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a stored hashed password."""
