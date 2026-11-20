"""Integration tests for Documents REST API endpoints."""

import io
import unittest
from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestDocumentAPI(unittest.TestCase):
    """Integration test suite for /documents endpoints."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            ai_provider="mock",
            strict_auth=True,
            jwt_secret_key="a" * 32,
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

        # Register User A
        self.client.post(
            "/auth/register",
            json={"email": "alice@example.com", "password": "Password123!"},
        )
        login_a = self.client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "Password123!"},
        )
        self.token_a = login_a.json()["access_token"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Register User B
        self.client.post(
            "/auth/register",
            json={"email": "bob@example.com", "password": "Password123!"},
        )
        login_b = self.client.post(
            "/auth/login",
            json={"email": "bob@example.com", "password": "Password123!"},
        )
        self.token_b = login_b.json()["access_token"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

    def test_upload_document_success(self) -> None:
        file_content = b"# Machine Learning Foundations\n- Linear Algebra\n- Calculus\n- PyTorch"
        files = {
            "file": ("syllabus.md", io.BytesIO(file_content), "text/markdown"),
        }
        res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["filename"], "syllabus.md")
        self.assertEqual(data["file_type"], "markdown")
        self.assertGreater(data["id"], 0)

    def test_upload_unsupported_file_type(self) -> None:
        files = {
            "file": ("program.exe", io.BytesIO(b"MZ12345"), "application/octet-stream"),
        }
        res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        self.assertEqual(res.status_code, 415)

    def test_upload_empty_file(self) -> None:
        files = {
            "file": ("empty.txt", io.BytesIO(b""), "text/plain"),
        }
        res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        self.assertEqual(res.status_code, 400)

    def test_list_and_get_documents(self) -> None:
        files = {
            "file": ("resume.txt", io.BytesIO(b"Backend Engineer with Go and AWS experience"), "text/plain"),
        }
        upload_res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        doc_id = upload_res.json()["id"]

        # List documents for Alice
        list_res = self.client.get("/documents", headers=self.headers_a)
        self.assertEqual(list_res.status_code, 200)
        docs = list_res.json()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["id"], doc_id)

        # Get document detail
        detail_res = self.client.get(f"/documents/{doc_id}", headers=self.headers_a)
        self.assertEqual(detail_res.status_code, 200)
        detail = detail_res.json()
        self.assertEqual(detail["id"], doc_id)
        self.assertIn("Backend Engineer", detail["extracted_text"])

        # Bob should not see Alice's document in list
        list_b = self.client.get("/documents", headers=self.headers_b)
        self.assertEqual(list_b.status_code, 200)
        self.assertEqual(list_b.json(), [])

        # Bob accessing Alice's document should return 403 Forbidden
        forbidden_res = self.client.get(f"/documents/{doc_id}", headers=self.headers_b)
        self.assertEqual(forbidden_res.status_code, 403)

    def test_summarize_document(self) -> None:
        files = {
            "file": ("spec.md", io.BytesIO(b"# Technical RFC\nDesign of real-time event pipeline."), "text/markdown"),
        }
        upload_res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        doc_id = upload_res.json()["id"]

        summary_res = self.client.post(f"/documents/{doc_id}/summarize", headers=self.headers_a)
        self.assertEqual(summary_res.status_code, 200)
        data = summary_res.json()
        self.assertEqual(data["id"], doc_id)
        self.assertEqual(data["filename"], "spec.md")
        self.assertTrue(len(data["summary"]) > 0)

    def test_delete_document(self) -> None:
        files = {
            "file": ("draft.txt", io.BytesIO(b"Draft document"), "text/plain"),
        }
        upload_res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        doc_id = upload_res.json()["id"]

        del_res = self.client.delete(f"/documents/{doc_id}", headers=self.headers_a)
        self.assertEqual(del_res.status_code, 204)

        # Verifying 404 after deletion
        get_res = self.client.get(f"/documents/{doc_id}", headers=self.headers_a)
        self.assertEqual(get_res.status_code, 404)

    def test_conversation_with_attached_document(self) -> None:
        # 1. Upload a document
        files = {
            "file": ("my_resume.txt", io.BytesIO(b"Candidate: Alice. 5 years Python, Docker, FastApi experience."), "text/plain"),
        }
        upload_res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        doc_id = upload_res.json()["id"]

        # 2. Create a conversation
        conv_res = self.client.post(
            "/conversations",
            json={"title": "Resume Career Planning"},
            headers=self.headers_a,
        )
        conv_id = conv_res.json()["id"]

        # 3. Send message with attached document_id
        msg_res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={
                "content": "Please review my attached resume and suggest a learning roadmap.",
                "document_id": doc_id,
            },
            headers=self.headers_a,
        )
        self.assertEqual(msg_res.status_code, 201)
        data = msg_res.json()
        self.assertIn("user_message", data)
        self.assertIn("assistant_message", data)
