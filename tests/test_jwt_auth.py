"""Unit and integration tests for JWT Authentication (Issue #32)."""

from datetime import timedelta
import unittest

from fastapi.testclient import TestClient

from masar.application.schemas.token import LoginRequestSchema, TokenResponseSchema
from masar.application.services.user_service import UserService
from masar.config.settings import Settings
from masar.container import build_user_service
from masar.domain.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from masar.domain.models import User
from masar.infrastructure.repositories.in_memory.user_repository import InMemoryUserRepository
from masar.infrastructure.security.jwt_token import JwtTokenService
from masar.infrastructure.security.password import Pbkdf2PasswordHasher
from masar.presentation.api.app import create_app


class TestJwtTokenService(unittest.TestCase):
    """Test JWT token encoding, decoding, and expiration logic."""

    def setUp(self) -> None:
        self.secret_key = "a" * 32  # 32-byte secret
        self.token_service = JwtTokenService(
            secret_key=self.secret_key,
            algorithm="HS256",
            expire_minutes=15,
        )

    def test_create_and_decode_valid_token(self) -> None:
        token = self.token_service.create_access_token(
            subject=42,
            claims={"email": "developer@masar.dev"},
        )
        self.assertIsInstance(token, str)
        payload = self.token_service.decode_access_token(token)
        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["email"], "developer@masar.dev")
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)

    def test_expired_token_raises_invalid_token_error(self) -> None:
        token = self.token_service.create_access_token(
            subject=1,
            expires_delta=timedelta(seconds=-10),  # expired 10 seconds ago
        )
        with self.assertRaises(InvalidTokenError) as ctx:
            self.token_service.decode_access_token(token)
        self.assertIn("expired", str(ctx.exception).lower())

    def test_invalid_signature_raises_invalid_token_error(self) -> None:
        token = self.token_service.create_access_token(subject=1)
        wrong_service = JwtTokenService(
            secret_key="b" * 32,
            algorithm="HS256",
        )
        with self.assertRaises(InvalidTokenError):
            wrong_service.decode_access_token(token)

    def test_malformed_token_raises_invalid_token_error(self) -> None:
        with self.assertRaises(InvalidTokenError):
            self.token_service.decode_access_token("not.a.valid.jwt.token")


class TestUserServiceLoginAndToken(unittest.TestCase):
    """Test user login and token decoding in UserService."""

    def setUp(self) -> None:
        self.user_repo = InMemoryUserRepository()
        self.hasher = Pbkdf2PasswordHasher()
        self.token_service = JwtTokenService(
            secret_key="secret" * 6,
            algorithm="HS256",
            expire_minutes=30,
        )
        self.user_service = UserService(
            user_repository=self.user_repo,
            password_hasher=self.hasher,
            token_service=self.token_service,
        )
        self.user = self.user_service.register_user("test@example.com", "Password123!")

    def test_login_successful_credentials(self) -> None:
        user, token = self.user_service.login_user("test@example.com", "Password123!")
        self.assertEqual(user.email, "test@example.com")
        self.assertIsInstance(token, str)

        decoded_user = self.user_service.get_user_from_token(token)
        self.assertEqual(decoded_user.id, user.id)
        self.assertEqual(decoded_user.email, user.email)

    def test_login_invalid_password_raises_invalid_credentials_error(self) -> None:
        with self.assertRaises(InvalidCredentialsError):
            self.user_service.login_user("test@example.com", "WrongPassword!")

    def test_login_nonexistent_email_raises_invalid_credentials_error(self) -> None:
        with self.assertRaises(InvalidCredentialsError):
            self.user_service.login_user("nonexistent@example.com", "Password123!")

    def test_get_user_from_token_inactive_user(self) -> None:
        inactive_user = self.user_service.register_user("inactive@example.com", "Password123!")
        inactive_user.is_active = False
        assert inactive_user.id is not None
        token = self.token_service.create_access_token(subject=inactive_user.id)
        with self.assertRaises(InvalidTokenError) as ctx:
            self.user_service.get_user_from_token(token)
        self.assertIn("inactive", str(ctx.exception).lower())

    def test_get_user_from_token_missing_subject(self) -> None:
        token = self.token_service.create_access_token(subject="")
        with self.assertRaises(InvalidTokenError):
            self.user_service.get_user_from_token(token)

    def test_get_user_from_token_nonexistent_user(self) -> None:
        token = self.token_service.create_access_token(subject=99999)
        with self.assertRaises(InvalidTokenError) as ctx:
            self.user_service.get_user_from_token(token)
        self.assertIn("no longer exists", str(ctx.exception).lower())


class TestAuthAPIEndpoints(unittest.TestCase):
    """Test API authentication endpoints (/auth/login, /auth/me)."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            jwt_secret_key="test-secret-key-that-is-at-least-32-bytes-long",
            jwt_expire_minutes=60,
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

        # Pre-register a test user
        self.reg_payload = {
            "email": "user@masar.dev",
            "password": "SecurePassword123!",
        }
        res = self.client.post("/auth/register", json=self.reg_payload)
        self.assertEqual(res.status_code, 201)

    def test_login_success_returns_jwt_token(self) -> None:
        login_payload = {
            "email": "USER@MASAR.DEV",  # case-insensitive check
            "password": "SecurePassword123!",
        }
        response = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

        # Verify password/secret are never in the response
        self.assertNotIn("password", data)
        self.assertNotIn("secret", str(data).lower())

    def test_login_invalid_password_returns_401(self) -> None:
        login_payload = {
            "email": "user@masar.dev",
            "password": "WrongPassword123!",
        }
        response = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_login_nonexistent_user_returns_401(self) -> None:
        login_payload = {
            "email": "missing@masar.dev",
            "password": "SecurePassword123!",
        }
        response = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 401)

    def test_get_current_user_profile_success(self) -> None:
        # Obtain token
        login_resp = self.client.post("/auth/login", json=self.reg_payload)
        token = login_resp.json()["access_token"]

        # Call /auth/me with Bearer token
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = self.client.get("/auth/me", headers=headers)
        self.assertEqual(me_resp.status_code, 200)
        data = me_resp.json()
        self.assertEqual(data["email"], "user@masar.dev")
        self.assertTrue(data["is_active"])
        self.assertNotIn("password", data)
        self.assertNotIn("hashed_password", data)

    def test_get_current_user_profile_missing_token_returns_401(self) -> None:
        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_get_current_user_profile_invalid_token_returns_401(self) -> None:
        headers = {"Authorization": "Bearer invalid.token.value"}
        response = self.client.get("/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)
