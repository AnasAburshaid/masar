"""Unit tests for DocumentService."""

import unittest

from masar.application.services.ai_service import AIService
from masar.application.services.document_service import DocumentService
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.exceptions.document import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    UnsupportedFileTypeError,
)
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.repositories.in_memory.document_repository import (
    InMemoryDocumentRepository,
)


class TestDocumentService(unittest.TestCase):
    """Test suite for DocumentService application workflows."""

    def setUp(self) -> None:
        self.repo = InMemoryDocumentRepository()
        self.mock_ai = MockAIProvider(
            default_response="Executive Summary: Senior backend engineer proficient in Python and Go.",
            default_model="mock-summary-model",
        )
        self.ai_service = AIService(ai_provider=self.mock_ai)
        self.service = DocumentService(
            document_repository=self.repo,
            ai_service=self.ai_service,
        )

    def test_upload_document_success(self) -> None:
        content = b"# Kubernetes Syllabus\n- Pods and Deployments\n- Services and Ingress"
        doc = self.service.upload_document(
            user_id=1,
            filename="syllabus.md",
            content_bytes=content,
        )
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.user_id, 1)
        self.assertEqual(doc.filename, "syllabus.md")
        self.assertEqual(doc.file_type, "markdown")
        self.assertEqual(doc.file_size_bytes, len(content))
        self.assertIn("Kubernetes Syllabus", doc.extracted_text)

    def test_upload_invalid_user_id(self) -> None:
        with self.assertRaises(InvalidIdError):
            self.service.upload_document(
                user_id=0,
                filename="test.txt",
                content_bytes=b"Hello",
            )

    def test_upload_unsupported_file_type(self) -> None:
        with self.assertRaises(UnsupportedFileTypeError):
            self.service.upload_document(
                user_id=1,
                filename="archive.zip",
                content_bytes=b"PK0304zipcontent",
            )

    def test_get_document_success(self) -> None:
        doc = self.service.upload_document(
            user_id=1,
            filename="notes.txt",
            content_bytes=b"Notes on system design.",
        )
        fetched = self.service.get_document(document_id=doc.id or 1, user_id=1)
        self.assertEqual(fetched.id, doc.id)
        self.assertEqual(fetched.filename, "notes.txt")

    def test_get_document_not_found(self) -> None:
        with self.assertRaises(DocumentNotFoundError):
            self.service.get_document(document_id=999, user_id=1)

    def test_get_document_access_denied_for_other_user(self) -> None:
        doc = self.service.upload_document(
            user_id=1,
            filename="secret_resume.txt",
            content_bytes=b"Confidential work history.",
        )
        with self.assertRaises(DocumentAccessDeniedError):
            self.service.get_document(document_id=doc.id or 1, user_id=2)

    def test_list_user_documents(self) -> None:
        self.service.upload_document(user_id=1, filename="doc1.txt", content_bytes=b"Doc 1")
        self.service.upload_document(user_id=1, filename="doc2.txt", content_bytes=b"Doc 2")
        self.service.upload_document(user_id=2, filename="doc3.txt", content_bytes=b"Doc 3")

        docs_1 = self.service.list_user_documents(user_id=1)
        self.assertEqual(len(docs_1), 2)
        filenames_1 = {d.filename for d in docs_1}
        self.assertEqual(filenames_1, {"doc1.txt", "doc2.txt"})

        docs_2 = self.service.list_user_documents(user_id=2)
        self.assertEqual(len(docs_2), 1)
        self.assertEqual(docs_2[0].filename, "doc3.txt")

    def test_delete_document_success(self) -> None:
        doc = self.service.upload_document(
            user_id=1, filename="to_delete.txt", content_bytes=b"Delete me"
        )
        deleted = self.service.delete_document(document_id=doc.id or 1, user_id=1)
        self.assertTrue(deleted)
        with self.assertRaises(DocumentNotFoundError):
            self.service.get_document(document_id=doc.id or 1, user_id=1)

    def test_delete_document_access_denied(self) -> None:
        doc = self.service.upload_document(
            user_id=1, filename="protected.txt", content_bytes=b"Protected"
        )
        with self.assertRaises(DocumentAccessDeniedError):
            self.service.delete_document(document_id=doc.id or 1, user_id=2)

    def test_summarize_document(self) -> None:
        doc = self.service.upload_document(
            user_id=1,
            filename="resume.txt",
            content_bytes=b"Senior Software Engineer with 8 years of experience in distributed systems.",
        )
        summary = self.service.summarize_document(document_id=doc.id or 1, user_id=1)
        self.assertIn("Senior backend engineer", summary)

        # Second call should return cached summary without calling AI
        cached_summary = self.service.summarize_document(document_id=doc.id or 1, user_id=1)
        self.assertEqual(cached_summary, summary)
