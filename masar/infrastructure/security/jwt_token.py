"""JWT token service implementation using PyJWT."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from masar.application.interfaces.security.token_service import TokenService
from masar.domain.exceptions import InvalidTokenError


class JwtTokenService(TokenService):
    """Generates and decodes JSON Web Tokens (JWT) for authentication."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = 60,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        subject: str | int,
        claims: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token for a subject."""
        now = datetime.now(timezone.utc)
        if expires_delta is not None:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self._expire_minutes)

        payload: dict[str, Any] = {
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        if claims:
            payload.update(claims)

        encoded: str = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return encoded

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a signed JWT access token, returning its payload."""
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise InvalidTokenError("Authentication token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError(f"Invalid authentication token: {exc}") from exc
        except Exception as exc:
            raise InvalidTokenError(f"Failed to decode authentication token: {exc}") from exc
