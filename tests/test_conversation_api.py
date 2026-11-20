"""Integration tests for Conversation and AI Chat REST API endpoints."""

import unittest
from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.presentation.api.app import create_app


class TestConversationAPI(unittest.TestCase):
    """Integration test suite for /conversations endpoints."""

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

    def test_create_and_list_conversations(self) -> None:
        # Create conversation
        res = self.client.post(
            "/conversations",
            json={"title": "Rust Learning Discussion"},
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["title"], "Rust Learning Discussion")
        self.assertGreater(data["id"], 0)

        # List conversations for User A
        list_res = self.client.get("/conversations", headers=self.headers_a)
        self.assertEqual(list_res.status_code, 200)
        convs = list_res.json()
        self.assertEqual(len(convs), 1)
        self.assertEqual(convs[0]["title"], "Rust Learning Discussion")

        # List conversations for User B (should be empty)
        list_b = self.client.get("/conversations", headers=self.headers_b)
        self.assertEqual(list_b.status_code, 200)
        self.assertEqual(list_b.json(), [])

    def test_get_conversation_detail(self) -> None:
        created = self.client.post(
            "/conversations",
            json={"title": "Cloud Architecture"},
            headers=self.headers_a,
        ).json()

        conv_id = created["id"]
        res = self.client.get(f"/conversations/{conv_id}", headers=self.headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["title"], "Cloud Architecture")
        self.assertEqual(data["messages"], [])

    def test_send_message_and_receive_reply(self) -> None:
        created = self.client.post(
            "/conversations",
            json={},
            headers=self.headers_a,
        ).json()
        conv_id = created["id"]

        # Send first message
        res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={"content": "What is the best way to learn Docker?"},
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["user_message"]["role"], "user")
        self.assertEqual(
            data["user_message"]["content"],
            "What is the best way to learn Docker?",
        )
        self.assertEqual(data["assistant_message"]["role"], "assistant")
        self.assertTrue(len(data["assistant_message"]["content"]) > 0)

        # Check detail includes both messages
        detail = self.client.get(
            f"/conversations/{conv_id}", headers=self.headers_a
        ).json()
        self.assertEqual(len(detail["messages"]), 2)
        # Title should have auto-updated
        self.assertIn("What is the best way to learn Docker", detail["title"])

    def test_update_conversation_title(self) -> None:
        created = self.client.post(
            "/conversations",
            json={"title": "Initial Title"},
            headers=self.headers_a,
        ).json()
        conv_id = created["id"]

        res = self.client.put(
            f"/conversations/{conv_id}",
            json={"title": "Updated Title"},
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["title"], "Updated Title")

    def test_delete_conversation(self) -> None:
        created = self.client.post(
            "/conversations",
            json={"title": "To Delete"},
            headers=self.headers_a,
        ).json()
        conv_id = created["id"]

        del_res = self.client.delete(
            f"/conversations/{conv_id}", headers=self.headers_a
        )
        self.assertEqual(del_res.status_code, 204)

        # Verify not found now
        get_res = self.client.get(
            f"/conversations/{conv_id}", headers=self.headers_a
        )
        self.assertEqual(get_res.status_code, 404)

    def test_cross_user_access_is_forbidden(self) -> None:
        created = self.client.post(
            "/conversations",
            json={"title": "Alice Secret Chat"},
            headers=self.headers_a,
        ).json()
        conv_id = created["id"]

        # User B attempts to view Alice's conversation
        view_res = self.client.get(
            f"/conversations/{conv_id}", headers=self.headers_b
        )
        self.assertEqual(view_res.status_code, 403)

        # User B attempts to send message to Alice's conversation
        send_res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={"content": "Intruder message"},
            headers=self.headers_b,
        )
        self.assertEqual(send_res.status_code, 403)

        # User B attempts to delete Alice's conversation
        del_res = self.client.delete(
            f"/conversations/{conv_id}", headers=self.headers_b
        )
        self.assertEqual(del_res.status_code, 403)

    def test_unauthenticated_request_rejected(self) -> None:
        res = self.client.get("/conversations")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
