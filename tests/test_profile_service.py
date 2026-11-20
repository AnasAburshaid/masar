"""Unit tests for ProfileService."""

import unittest

from masar.application.services.ai_service import AIService
from masar.application.services.document_service import DocumentService
from masar.application.services.profile_service import ProfileService
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.exceptions.profile import (
    ProfileAccessDeniedError,
    ProfileItemNotFoundError,
)
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.repositories.in_memory.document_repository import (
    InMemoryDocumentRepository,
)
from masar.infrastructure.repositories.in_memory.profile_repository import (
    InMemoryProfileRepository,
)


class TestProfileService(unittest.TestCase):
    """Test suite for ProfileService application workflows."""

    def setUp(self) -> None:
        self.profile_repo = InMemoryProfileRepository()
        self.doc_repo = InMemoryDocumentRepository()
        self.mock_ai = MockAIProvider(
            default_response='{"items": [{"name": "FastAPI", "category": "technology", "level": "intermediate"}, {"name": "Python", "category": "language", "level": "advanced"}, {"name": "Microservices", "category": "goal", "level": "beginner"}]}',
            default_model="mock-profile-extractor",
        )
        self.ai_service = AIService(ai_provider=self.mock_ai)
        self.doc_service = DocumentService(
            document_repository=self.doc_repo,
            ai_service=self.ai_service,
        )
        self.service = ProfileService(
            profile_repository=self.profile_repo,
            ai_service=self.ai_service,
            document_repository=self.doc_repo,
        )

    def test_get_empty_profile(self) -> None:
        profile = self.service.get_profile(user_id=1)
        self.assertEqual(profile.user_id, 1)
        self.assertEqual(profile.bio, "")
        self.assertEqual(len(profile.items), 0)
        self.assertEqual(profile.total_items, 0)

    def test_add_manual_item(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="Python",
            category="language",
            level="advanced",
            is_confirmed=True,
        )
        self.assertIsNotNone(item.id)
        self.assertEqual(item.name, "Python")
        self.assertEqual(item.category, "language")
        self.assertEqual(item.level, "advanced")
        self.assertTrue(item.is_confirmed)
        self.assertEqual(item.source_type, "manual")

        profile = self.service.get_profile(user_id=1)
        self.assertEqual(len(profile.confirmed_items), 1)
        self.assertEqual(len(profile.inferred_items), 0)
        self.assertEqual(profile.total_items, 1)

    def test_confirm_item(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="Docker",
            category="technology",
            level="intermediate",
            is_confirmed=False,
            source_type="conversation",
        )
        self.assertFalse(item.is_confirmed)

        confirmed = self.service.confirm_item(user_id=1, item_id=item.id or 1)
        self.assertTrue(confirmed.is_confirmed)

    def test_confirm_item_access_denied(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="Rust",
            category="language",
            is_confirmed=False,
        )
        with self.assertRaises(ProfileAccessDeniedError):
            self.service.confirm_item(user_id=2, item_id=item.id or 1)

    def test_confirm_item_not_found(self) -> None:
        with self.assertRaises(ProfileItemNotFoundError):
            self.service.confirm_item(user_id=1, item_id=999)

    def test_update_item_success(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="PostgreSQL",
            category="technology",
            level="beginner",
        )
        updated = self.service.update_item(
            user_id=1,
            item_id=item.id or 1,
            level="advanced",
        )
        self.assertEqual(updated.level, "advanced")

    def test_update_item_forbidden(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="Go",
            category="language",
        )
        with self.assertRaises(ProfileAccessDeniedError):
            self.service.update_item(
                user_id=2,
                item_id=item.id or 1,
                name="Golang",
            )

    def test_delete_item_success(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="React",
            category="technology",
        )
        res = self.service.delete_item(user_id=1, item_id=item.id or 1)
        self.assertTrue(res)

        profile = self.service.get_profile(user_id=1)
        self.assertEqual(len(profile.items), 0)

    def test_delete_item_forbidden(self) -> None:
        item = self.service.add_item(
            user_id=1,
            name="Kubernetes",
            category="technology",
        )
        with self.assertRaises(ProfileAccessDeniedError):
            self.service.delete_item(user_id=2, item_id=item.id or 1)

    def test_update_bio(self) -> None:
        self.service.update_bio(user_id=1, bio="Staff Backend Engineer specializing in Distributed Systems.")
        profile = self.service.get_profile(user_id=1)
        self.assertEqual(profile.bio, "Staff Backend Engineer specializing in Distributed Systems.")

    def test_extract_from_document(self) -> None:
        doc = self.doc_service.upload_document(
            user_id=1,
            filename="resume.md",
            content_bytes=b"# Resume\nSkilled in Python, FastAPI, and Microservices.",
        )
        extracted = self.service.extract_from_document(user_id=1, document_id=doc.id or 1)
        self.assertEqual(len(extracted), 3)

        for item in extracted:
            self.assertFalse(item.is_confirmed)  # Must be unconfirmed until user confirms
            self.assertEqual(item.source_type, "document")
            self.assertEqual(item.source_id, doc.id)

        profile = self.service.get_profile(user_id=1)
        self.assertEqual(len(profile.inferred_items), 3)
        self.assertEqual(len(profile.confirmed_items), 0)

    def test_extract_from_document_forbidden(self) -> None:
        doc = self.doc_service.upload_document(
            user_id=1,
            filename="resume.md",
            content_bytes=b"Confidential resume",
        )
        with self.assertRaises(ProfileAccessDeniedError):
            self.service.extract_from_document(user_id=2, document_id=doc.id or 1)


if __name__ == "__main__":
    unittest.main()
