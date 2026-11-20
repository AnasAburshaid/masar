"""Integration tests for Recommendations REST API endpoints."""

import unittest
from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestRecommendationAPI(unittest.TestCase):
    """Integration test suite for /recommendations endpoints."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            ai_provider="mock",
            strict_auth=True,
            jwt_secret_key="a" * 32,
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

        # Register and log in User A
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

    def test_get_recommendations_empty_state(self) -> None:
        res = self.client.get("/recommendations", headers=self.headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_completed_topics"], 0)
        self.assertEqual(data["total_in_progress_topics"], 0)
        self.assertEqual(data["active_journey_titles"], [])
        self.assertEqual(data["recommendations"], [])
        self.assertEqual(data["knowledge_gaps"], [])

    def test_get_recommendations_with_journey_and_topics(self) -> None:
        # Create journey, section, topics
        j_res = self.client.post(
            "/journeys",
            json={"title": "Cloud Native Architecture"},
            headers=self.headers_a,
        )
        j_id = j_res.json()["id"]

        s_res = self.client.post(
            "/sections",
            json={"journey_id": j_id, "title": "Microservices"},
            headers=self.headers_a,
        )
        s_id = s_res.json()["id"]

        t1_res = self.client.post(
            "/topics",
            json={"section_id": s_id, "title": "Service Discovery"},
            headers=self.headers_a,
        )
        t1_id = t1_res.json()["id"]

        self.client.post(
            "/topics",
            json={"section_id": s_id, "title": "Circuit Breakers"},
            headers=self.headers_a,
        )

        # Mark topic 1 complete
        self.client.patch(f"/topics/{t1_id}/complete", headers=self.headers_a)

        # Add profile goal
        self.client.post(
            "/profile/items",
            json={"name": "Event-Driven Messaging", "category": "goal", "is_confirmed": True},
            headers=self.headers_a,
        )

        # Fetch recommendations
        rec_res = self.client.get("/recommendations", headers=self.headers_a)
        self.assertEqual(rec_res.status_code, 200)
        data = rec_res.json()
        self.assertEqual(data["total_completed_topics"], 1)
        self.assertEqual(data["total_in_progress_topics"], 1)
        self.assertIn("Cloud Native Architecture", data["active_journey_titles"])

        # Should recommend Circuit Breakers next
        recs = data["recommendations"]
        self.assertGreater(len(recs), 0)
        next_topic = next((r for r in recs if r["recommendation_type"] == "next_topic"), None)
        self.assertIsNotNone(next_topic)
        assert next_topic is not None
        self.assertIn("Circuit Breakers", next_topic["title"])
        self.assertIn("Microservices", next_topic["reason"])
        self.assertIn("50%", next_topic["reason"])

        # Should identify gap for profile goal
        gaps = data["knowledge_gaps"]
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["topic_name"], "Event-Driven Messaging")

    def test_propose_journey_improvements(self) -> None:
        j_res = self.client.post(
            "/journeys",
            json={"title": "Go Fundamentals"},
            headers=self.headers_a,
        )
        j_id = j_res.json()["id"]

        # Configure mock AI response
        ai_provider = self.app.state.ai_service._provider
        ai_provider.enqueue_response(
            '{"improvements": [{"title": "Goroutines and Channels", "reason": "Fundamental for concurrency."}]}'
        )

        res = self.client.post(
            f"/recommendations/improve/{j_id}",
            json={"feedback": "Need to understand concurrency primitives."},
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Goroutines and Channels")
        self.assertIn("concurrency", items[0]["reason"])

    def test_unauthenticated_request_fails(self) -> None:
        res = self.client.get("/recommendations")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
