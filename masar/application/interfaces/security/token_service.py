"""Token service abstraction."""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any


class TokenService(ABC):
    """Abstract interface for generating and decoding access tokens."""

    @abstractmethod
    def create_access_token(
        self,
        subject: str | int,
        claims: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token for a subject."""

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a signed JWT access token, returning its payload."""
