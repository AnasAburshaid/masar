"""Unit and integration tests for User Registration and Authentication Foundation."""

import unittest
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from masar.application.interfaces.repositories.user_repository import UserRepository
from masar.application.schemas.user import UserRegisterSchema, UserResponseSchema
from masar.application.services.user_service import UserService
from masar.config.settings import Settings
from masar.container import build_user_service
from masar.domain.exceptions import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from masar.domain.models import User
from masar.infrastructure.database.models import UserModel
from masar.infrastructure.database.session import Base
from masar.infrastructure.repositories.database.user_repository import SqlUserRepository
from masar.infrastructure.repositories.in_memory.user_repository import InMemoryUserRepository
from masar.infrastructure.security.password import (
    Pbkdf2PasswordHasher,
    hash_password,
    verify_password,
)
from masar.presentation.api.app import create_app


class TestUserDomainModel(unittest.TestCase):
    """Test User domain entity validation and business rules."""

    def test_valid_user_creation(self) -> None:
        user = User(
            email="Learner@Example.Com",
            hashed_password="pbkdf2:sha256:100000$salt$hash",
        )
        self.assertEqual(user.email, "learner@example.com")
        self.assertFalse(user.is_persisted)
        self.assertTrue(user.is_active)
        self.assertIn("learner@example.com", str(user))

    def test_invalid_email_format_raises_validation_error(self) -> None:
        invalid_emails = ["notanemail", "user@", "@domain.com", "user@domain", "user space@domain.com"]
        for bad_email in invalid_emails:
            with self.subTest(email=bad_email):
                with self.assertRaises(ValidationError):
                    User(email=bad_email, hashed_password="hashed_secret")

    def test_empty_email_raises_empty_field_error(self) -> None:
        with self.assertRaises(EmptyFieldError):
            User(email="   ", hashed_password="hashed_secret")

    def test_excessive_email_length_raises_field_length_error(self) -> None:
        long_email = "a" * 250 + "@example.com"
        with self.assertRaises(FieldLengthError):
            User(email=long_email, hashed_password="hashed_secret")

    def test_empty_hashed_password_raises_empty_field_error(self) -> None:
        with self.assertRaises(EmptyFieldError):
            User(email="valid@example.com", hashed_password="   ")

    def test_invalid_id_raises_invalid_id_error(self) -> None:
        with self.assertRaises(InvalidIdError):
            User(id=0, email="valid@example.com", hashed_password="hashed_secret")
        with self.assertRaises(InvalidIdError):
            User(id=-5, email="valid@example.com", hashed_password="hashed_secret")


class TestPasswordSecurity(unittest.TestCase):
    """Test secure password hashing and verification."""

    def test_password_hashing_and_verification(self) -> None:
        plain = "SuperSecurePassword123!"
        hashed = hash_password(plain)
        self.assertIn("pbkdf2:sha256:", hashed)
        self.assertNotEqual(plain, hashed)
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_salts_are_unique_per_hash(self) -> None:
        plain = "SamePasswordAcrossUsers"
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)
        self.assertNotEqual(hash1, hash2)
        self.assertTrue(verify_password(plain, hash1))
        self.assertTrue(verify_password(plain, hash2))

    def test_verify_password_rejects_malformed_hashes(self) -> None:
        self.assertFalse(verify_password("secret", "malformed_hash"))
        self.assertFalse(verify_password("secret", ""))
        self.assertFalse(verify_password("", "pbkdf2:sha256:100000$salt$hash"))

    def test_empty_password_hashing_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            hash_password("")


class TestUserRepositoryImplementations(unittest.TestCase):
    """Test InMemoryUserRepository and SqlUserRepository behavior."""

    def _test_repository_crud(self, repo: UserRepository) -> None:
        # Add user
        user = User(email="test@masar.dev", hashed_password=hash_password("password123"))
        saved = repo.add(user)
        self.assertIsNotNone(saved.id)
        assert saved.id is not None
        self.assertEqual(saved.email, "test@masar.dev")

        # Get by ID
        fetched = repo.get_by_id(saved.id)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.email, "test@masar.dev")

        # Get by Email (case-insensitive)
        by_email = repo.get_by_email("TEST@MASAR.DEV")
        self.assertIsNotNone(by_email)
        assert by_email is not None
        self.assertEqual(by_email.id, saved.id)

        # Non-existent
        self.assertIsNone(repo.get_by_id(9999))
        self.assertIsNone(repo.get_by_email("unknown@masar.dev"))

        # Duplicate email rejection
        dup = User(email="test@masar.dev", hashed_password=hash_password("differentpass"))
        with self.assertRaises(UserAlreadyExistsError):
            repo.add(dup)

        # Get all
        repo.add(User(email="second@masar.dev", hashed_password=hash_password("password123")))
        all_users = repo.get_all()
        self.assertEqual(len(all_users), 2)

        # Delete
        self.assertTrue(repo.delete(saved.id))
        self.assertFalse(repo.delete(saved.id))
        self.assertIsNone(repo.get_by_id(saved.id))

    def test_in_memory_user_repository(self) -> None:
        repo = InMemoryUserRepository()
        self._test_repository_crud(repo)

    def test_sql_user_repository(self) -> None:
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session: Session = session_factory()
        try:
            repo = SqlUserRepository(session)
            self._test_repository_crud(repo)
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)


class TestUserService(unittest.TestCase):
    """Test UserService business orchestration and registration rules."""

    def setUp(self) -> None:
        self.repo = InMemoryUserRepository()
        self.hasher = Pbkdf2PasswordHasher()
        self.service = UserService(user_repository=self.repo, password_hasher=self.hasher)

    def test_register_user_success(self) -> None:
        user = self.service.register_user("developer@example.com", "ValidSecretPassword1")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "developer@example.com")
        self.assertNotEqual(user.hashed_password, "ValidSecretPassword1")
        self.assertTrue(verify_password("ValidSecretPassword1", user.hashed_password))

    def test_register_duplicate_email_raises_error(self) -> None:
        self.service.register_user("dev@example.com", "Password123")
        with self.assertRaises(UserAlreadyExistsError):
            self.service.register_user("dev@example.com", "AnotherPassword123")
        with self.assertRaises(UserAlreadyExistsError):
            self.service.register_user("DEV@EXAMPLE.COM", "AnotherPassword123")

    def test_register_short_password_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.register_user("dev@example.com", "short")

    def test_get_user_methods(self) -> None:
        created = self.service.register_user("alice@example.com", "Password123")
        assert created.id is not None
        fetched = self.service.get_user_by_id(created.id)
        self.assertEqual(fetched.email, "alice@example.com")
        by_email = self.service.get_user_by_email("ALICE@EXAMPLE.COM")
        self.assertEqual(by_email.id, created.id)

        with self.assertRaises(UserNotFoundError):
            self.service.get_user_by_id(9999)
        with self.assertRaises(UserNotFoundError):
            self.service.get_user_by_email("missing@example.com")

    def test_authenticate_user(self) -> None:
        self.service.register_user("auth@example.com", "MySecretP@ss")
        # Correct credentials
        authenticated = self.service.authenticate_user("auth@example.com", "MySecretP@ss")
        self.assertIsNotNone(authenticated)
        # Wrong password
        self.assertIsNone(self.service.authenticate_user("auth@example.com", "WrongPassword"))
        # Non-existent email
        self.assertIsNone(self.service.authenticate_user("none@example.com", "MySecretP@ss"))


class TestUserAuthAPI(unittest.TestCase):
    """Test user registration endpoint via FastAPI TestClient."""

    def test_api_registration_success(self) -> None:
        settings = Settings(storage_type="in_memory")
        app = create_app(settings)
        client = TestClient(app)

        payload = {
            "email": "newuser@masar.dev",
            "password": "SecurePassword123!",
        }
        response = client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["email"], "newuser@masar.dev")
        self.assertTrue(data["is_active"])
        self.assertIn("created_at", data)
        # Verify passwords are NEVER returned in response
        self.assertNotIn("password", data)
        self.assertNotIn("hashed_password", data)

    def test_api_registration_duplicate_email_returns_409(self) -> None:
        settings = Settings(storage_type="in_memory")
        app = create_app(settings)
        client = TestClient(app)

        payload = {
            "email": "existing@masar.dev",
            "password": "SecurePassword123!",
        }
        res1 = client.post("/auth/register", json=payload)
        self.assertEqual(res1.status_code, 201)

        res2 = client.post("/auth/register", json=payload)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("already exists", res2.json()["detail"])

    def test_api_registration_short_password_returns_422(self) -> None:
        settings = Settings(storage_type="in_memory")
        app = create_app(settings)
        client = TestClient(app)

        payload = {
            "email": "shortpass@masar.dev",
            "password": "short",
        }
        response = client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_api_registration_invalid_email_returns_422(self) -> None:
        settings = Settings(storage_type="in_memory")
        app = create_app(settings)
        client = TestClient(app)

        payload = {
            "email": "invalid-email-format",
            "password": "ValidPassword123!",
        }
        response = client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_api_registration_with_database_persistence(self) -> None:
        settings = Settings(
            storage_type="database",
            database_url="sqlite://",
        )
        app = create_app(settings)
        client = TestClient(app)

        payload = {
            "email": "dbuser@masar.dev",
            "password": "DatabaseUserPassword123!",
        }
        response = client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "dbuser@masar.dev")

        # Duplicate rejection in database
        dup_response = client.post("/auth/register", json=payload)
        self.assertEqual(dup_response.status_code, 409)
