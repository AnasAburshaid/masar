"""Integration tests for AI Action Proposal REST API endpoints."""

import json
import unittest
from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.presentation.api.app import create_app


class TestActionAPI(unittest.TestCase):
    """Integration test suite for action proposal endpoints."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            ai_provider="mock",
            strict_auth=True,
            jwt_secret_key="b" * 32,
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

        # Register User A (Alice)
        self.client.post(
            "/auth/register",
            json={"email": "alice_action@example.com", "password": "Password123!"},
        )
        login_a = self.client.post(
            "/auth/login",
            json={"email": "alice_action@example.com", "password": "Password123!"},
        )
        self.token_a = login_a.json()["access_token"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Register User B (Bob)
        self.client.post(
            "/auth/register",
            json={"email": "bob_action@example.com", "password": "Password123!"},
        )
        login_b = self.client.post(
            "/auth/login",
            json={"email": "bob_action@example.com", "password": "Password123!"},
        )
        self.token_b = login_b.json()["access_token"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

    def test_send_message_triggers_action_proposal(self) -> None:
        # Create conversation
        conv_res = self.client.post(
            "/conversations",
            json={"title": "Cloud Study"},
            headers=self.headers_a,
        )
        conv_id = conv_res.json()["id"]

        # Configure mock AI to output a proposal block
        mock_ai: MockAIProvider = self.app.state.ai_service._provider
        proposal_payload = {
            "action_proposal": {
                "title": "Setup Kubernetes Journey",
                "actions": [
                    {
                        "tool": "create_journey",
                        "description": "Create Kubernetes Mastery journey",
                        "parameters": {"title": "Kubernetes Mastery", "description": "Cloud native"},
                    },
                    {
                        "tool": "create_section",
                        "description": "Add Architecture section",
                        "parameters": {"journey_id": "$0.id", "title": "Cluster Architecture"},
                    },
                ],
            }
        }
        mock_ai.enqueue_response(
            f"I have designed a Kubernetes path for you.\n\n```json\n{json.dumps(proposal_payload)}\n```"
        )

        msg_res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={"content": "Plan a Kubernetes roadmap for me"},
            headers=self.headers_a,
        )
        self.assertEqual(msg_res.status_code, 201)
        data = msg_res.json()

        self.assertIsNotNone(data["action_proposal"])
        proposal = data["action_proposal"]
        self.assertEqual(proposal["title"], "Setup Kubernetes Journey")
        self.assertEqual(proposal["status"], "pending")
        self.assertEqual(len(proposal["actions"]), 2)
        proposal_id = proposal["id"]

        # List proposals for conversation
        list_res = self.client.get(
            f"/conversations/{conv_id}/proposals",
            headers=self.headers_a,
        )
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.json()), 1)

        # Get specific proposal detail
        detail_res = self.client.get(
            f"/conversations/{conv_id}/proposals/{proposal_id}",
            headers=self.headers_a,
        )
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()["title"], "Setup Kubernetes Journey")

        # Approve and execute proposal
        approve_res = self.client.post(
            f"/conversations/{conv_id}/proposals/{proposal_id}/approve",
            headers=self.headers_a,
        )
        self.assertEqual(approve_res.status_code, 200)
        approve_data = approve_res.json()
        self.assertEqual(approve_data["executed_count"], 2)
        self.assertEqual(approve_data["failed_count"], 0)
        self.assertEqual(approve_data["proposal"]["status"], "executed")

        # Verify real backend entity was created
        journeys_res = self.client.get("/journeys", headers=self.headers_a)
        self.assertEqual(journeys_res.status_code, 200)
        journeys = journeys_res.json()
        self.assertEqual(len(journeys), 1)
        self.assertEqual(journeys[0]["title"], "Kubernetes Mastery")

    def test_reject_proposal_workflow(self) -> None:
        conv_res = self.client.post(
            "/conversations",
            json={"title": "To Reject"},
            headers=self.headers_a,
        )
        conv_id = conv_res.json()["id"]

        mock_ai: MockAIProvider = self.app.state.ai_service._provider
        proposal_payload = {
            "action_proposal": {
                "title": "Unwanted Action",
                "actions": [
                    {
                        "tool": "create_journey",
                        "description": "Bad journey",
                        "parameters": {"title": "Bad Journey"},
                    }
                ],
            }
        }
        mock_ai.enqueue_response(f"Here is a plan:\n\n```json\n{json.dumps(proposal_payload)}\n```")

        msg_res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={"content": "Suggest something"},
            headers=self.headers_a,
        )
        proposal_id = msg_res.json()["action_proposal"]["id"]

        # Reject proposal
        reject_res = self.client.post(
            f"/conversations/{conv_id}/proposals/{proposal_id}/reject",
            headers=self.headers_a,
        )
        self.assertEqual(reject_res.status_code, 200)
        self.assertEqual(reject_res.json()["status"], "rejected")

        # Ensure journey was NOT created
        journeys = self.client.get("/journeys", headers=self.headers_a).json()
        self.assertEqual(journeys, [])

    def test_user_isolation_blocks_unauthorized_approval(self) -> None:
        conv_res = self.client.post(
            "/conversations",
            json={"title": "Alice's Secret Plan"},
            headers=self.headers_a,
        )
        conv_id = conv_res.json()["id"]

        mock_ai: MockAIProvider = self.app.state.ai_service._provider
        proposal_payload = {
            "action_proposal": {
                "title": "Alice's Plan",
                "actions": [
                    {
                        "tool": "create_journey",
                        "parameters": {"title": "Alice's Journey"},
                    }
                ],
            }
        }
        mock_ai.enqueue_response(f"Plan:\n\n```json\n{json.dumps(proposal_payload)}\n```")

        msg_res = self.client.post(
            f"/conversations/{conv_id}/messages",
            json={"content": "Hi"},
            headers=self.headers_a,
        )
        proposal_id = msg_res.json()["action_proposal"]["id"]

        # Bob attempts to approve Alice's proposal -> 403 Forbidden
        bob_approve = self.client.post(
            f"/conversations/{conv_id}/proposals/{proposal_id}/approve",
            headers=self.headers_b,
        )
        self.assertEqual(bob_approve.status_code, 403)

        # Bob attempts to reject Alice's proposal -> 403 Forbidden
        bob_reject = self.client.post(
            f"/conversations/{conv_id}/proposals/{proposal_id}/reject",
            headers=self.headers_b,
        )
        self.assertEqual(bob_reject.status_code, 403)


if __name__ == "__main__":
    unittest.main()
