"""Integration tests for Learning Profile REST API endpoints."""

import io
import unittest
from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestProfileAPI(unittest.TestCase):
    """Integration test suite for /profile endpoints."""

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

    def test_get_profile_initial_state(self) -> None:
        res = self.client.get("/profile", headers=self.headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["bio"], "")
        self.assertEqual(data["total_items"], 0)
        self.assertEqual(data["confirmed_items"], [])
        self.assertEqual(data["inferred_items"], [])

    def test_update_bio(self) -> None:
        res = self.client.put(
            "/profile/bio",
            json={"bio": "Full stack engineer passionate about systems architecture."},
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["bio"], "Full stack engineer passionate about systems architecture.")

    def test_add_and_update_profile_item(self) -> None:
        # Add item
        add_res = self.client.post(
            "/profile/items",
            json={
                "name": "TypeScript",
                "category": "language",
                "level": "intermediate",
                "is_confirmed": True,
            },
            headers=self.headers_a,
        )
        self.assertEqual(add_res.status_code, 201)
        item = add_res.json()
        self.assertEqual(item["name"], "TypeScript")
        self.assertTrue(item["is_confirmed"])
        item_id = item["id"]

        # Update item
        update_res = self.client.put(
            f"/profile/items/{item_id}",
            json={"level": "advanced"},
            headers=self.headers_a,
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["level"], "advanced")

        # Confirm User B cannot update User A's item
        forbidden_res = self.client.put(
            f"/profile/items/{item_id}",
            json={"level": "beginner"},
            headers=self.headers_b,
        )
        self.assertEqual(forbidden_res.status_code, 403)

    def test_confirm_item(self) -> None:
        # Add unconfirmed item
        add_res = self.client.post(
            "/profile/items",
            json={
                "name": "GraphQL",
                "category": "technology",
                "level": "beginner",
                "is_confirmed": False,
            },
            headers=self.headers_a,
        )
        item_id = add_res.json()["id"]

        # User B trying to confirm fails
        forbidden_res = self.client.post(
            f"/profile/items/{item_id}/confirm",
            headers=self.headers_b,
        )
        self.assertEqual(forbidden_res.status_code, 403)

        # User A confirms
        confirm_res = self.client.post(
            f"/profile/items/{item_id}/confirm",
            headers=self.headers_a,
        )
        self.assertEqual(confirm_res.status_code, 200)
        self.assertTrue(confirm_res.json()["is_confirmed"])

    def test_delete_item(self) -> None:
        add_res = self.client.post(
            "/profile/items",
            json={"name": "Ruby", "category": "language", "is_confirmed": True},
            headers=self.headers_a,
        )
        item_id = add_res.json()["id"]

        # User B delete fails
        forbidden_res = self.client.delete(f"/profile/items/{item_id}", headers=self.headers_b)
        self.assertEqual(forbidden_res.status_code, 403)

        # User A delete succeeds
        del_res = self.client.delete(f"/profile/items/{item_id}", headers=self.headers_a)
        self.assertEqual(del_res.status_code, 204)

        # Verify gone
        profile_res = self.client.get("/profile", headers=self.headers_a)
        self.assertEqual(profile_res.json()["total_items"], 0)

    def test_extract_profile_from_document(self) -> None:
        # Enqueue response for mock AI
        self.app.state.ai_service._provider.enqueue_response(
            '{"items": [{"name": "FastAPI", "category": "technology", "level": "intermediate"}]}'
        )

        # Upload doc as User A
        content = b"# Resume\nSkilled in Python, FastAPI, and Cloud Architecture."
        files = {
            "file": ("resume.md", io.BytesIO(content), "text/markdown"),
        }
        up_res = self.client.post("/documents/upload", files=files, headers=self.headers_a)
        self.assertEqual(up_res.status_code, 201)
        doc_id = up_res.json()["id"]

        # User B cannot extract from User A's document
        forbidden_res = self.client.post(
            f"/profile/extract/document/{doc_id}",
            headers=self.headers_b,
        )
        self.assertEqual(forbidden_res.status_code, 403)

        # User A extracts successfully
        extract_res = self.client.post(
            f"/profile/extract/document/{doc_id}",
            headers=self.headers_a,
        )
        self.assertEqual(extract_res.status_code, 200)
        data = extract_res.json()
        self.assertEqual(data["source_type"], "document")
        self.assertEqual(data["source_id"], doc_id)
        self.assertGreater(len(data["extracted_items"]), 0)
        for item in data["extracted_items"]:
            self.assertFalse(item["is_confirmed"])


if __name__ == "__main__":
    unittest.main()
