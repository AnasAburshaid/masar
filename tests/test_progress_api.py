"""Integration tests for Progress REST API endpoints and end-to-end learning workflows."""

import unittest

from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestProgressAPI(unittest.TestCase):
    """Test suite for Progress API endpoints and workflow testing."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            environment="testing",
        )
        self.app = create_app(settings=self.settings)
        self.client = TestClient(self.app)

    def test_progress_empty_journey(self) -> None:
        journey = self.client.post("/journeys", json={"title": "Empty Track"}).json()
        j_id = journey["id"]

        resp = self.client.get(f"/journeys/{j_id}/progress")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["journey_id"], j_id)
        self.assertEqual(data["title"], "Empty Track")
        self.assertEqual(data["total_topics"], 0)
        self.assertEqual(data["completed_topics"], 0)
        self.assertEqual(data["percentage"], 0.0)
        self.assertFalse(data["is_complete"])
        self.assertEqual(data["sections"], [])

    def test_progress_journey_with_empty_section(self) -> None:
        journey = self.client.post("/journeys", json={"title": "Track with Empty Section"}).json()
        j_id = journey["id"]
        sec = self.client.post("/sections", json={"journey_id": j_id, "title": "Empty Section"}).json()
        sec_id = sec["id"]

        # Journey progress
        resp = self.client.get(f"/journeys/{j_id}/progress")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_topics"], 0)
        self.assertEqual(len(data["sections"]), 1)
        self.assertEqual(data["sections"][0]["total_topics"], 0)
        self.assertEqual(data["sections"][0]["percentage"], 0.0)

        # Section progress directly
        sec_resp = self.client.get(f"/sections/{sec_id}/progress")
        self.assertEqual(sec_resp.status_code, 200)
        sec_data = sec_resp.json()
        self.assertEqual(sec_data["section_id"], sec_id)
        self.assertEqual(sec_data["total_topics"], 0)
        self.assertEqual(sec_data["completed_topics"], 0)
        self.assertFalse(sec_data["is_complete"])

    def test_progress_updates_dynamically_when_topics_change(self) -> None:
        # 1. Create Journey
        j_id = self.client.post("/journeys", json={"title": "FastAPI Track"}).json()["id"]

        # 2. Create Section
        s_id = self.client.post("/sections", json={"journey_id": j_id, "title": "Routing"}).json()["id"]

        # 3. Add 2 Topics
        t1_id = self.client.post("/topics", json={"section_id": s_id, "title": "Path Ops"}).json()["id"]
        t2_id = self.client.post("/topics", json={"section_id": s_id, "title": "Query Params"}).json()["id"]

        # 4. Check initial progress (0%)
        initial_prog = self.client.get(f"/journeys/{j_id}/progress").json()
        self.assertEqual(initial_prog["total_topics"], 2)
        self.assertEqual(initial_prog["completed_topics"], 0)
        self.assertEqual(initial_prog["percentage"], 0.0)
        self.assertFalse(initial_prog["is_complete"])

        # 5. Complete topic 1 -> 50%
        self.client.patch(f"/topics/{t1_id}/complete")
        half_prog = self.client.get(f"/journeys/{j_id}/progress").json()
        self.assertEqual(half_prog["completed_topics"], 1)
        self.assertEqual(half_prog["percentage"], 50.0)
        self.assertFalse(half_prog["is_complete"])

        # 6. Complete topic 2 -> 100%
        self.client.patch(f"/topics/{t2_id}/complete")
        full_prog = self.client.get(f"/journeys/{j_id}/progress").json()
        self.assertEqual(full_prog["completed_topics"], 2)
        self.assertEqual(full_prog["percentage"], 100.0)
        self.assertTrue(full_prog["is_complete"])

        # 7. Uncomplete topic 1 -> back to 50%
        self.client.patch(f"/topics/{t1_id}/pending")
        back_prog = self.client.get(f"/journeys/{j_id}/progress").json()
        self.assertEqual(back_prog["completed_topics"], 1)
        self.assertEqual(back_prog["percentage"], 50.0)
        self.assertFalse(back_prog["is_complete"])

    def test_multiple_sections_progress_breakdown(self) -> None:
        j_id = self.client.post("/journeys", json={"title": "Fullstack"}).json()["id"]

        # Section 1: 2 topics, 2 completed (100%)
        s1_id = self.client.post("/sections", json={"journey_id": j_id, "title": "Frontend"}).json()["id"]
        t1 = self.client.post("/topics", json={"section_id": s1_id, "title": "HTML"}).json()["id"]
        t2 = self.client.post("/topics", json={"section_id": s1_id, "title": "CSS"}).json()["id"]
        self.client.patch(f"/topics/{t1}/complete")
        self.client.patch(f"/topics/{t2}/complete")

        # Section 2: 2 topics, 0 completed (0%)
        s2_id = self.client.post("/sections", json={"journey_id": j_id, "title": "Backend"}).json()["id"]
        self.client.post("/topics", json={"section_id": s2_id, "title": "FastAPI"})
        self.client.post("/topics", json={"section_id": s2_id, "title": "Databases"})

        # Overall: 2 of 4 completed = 50%
        prog = self.client.get(f"/journeys/{j_id}/progress").json()
        self.assertEqual(prog["total_topics"], 4)
        self.assertEqual(prog["completed_topics"], 2)
        self.assertEqual(prog["percentage"], 50.0)
        self.assertFalse(prog["is_complete"])

        # Verify sections breakdown
        self.assertEqual(len(prog["sections"]), 2)
        sec1_info = next(s for s in prog["sections"] if s["section_id"] == s1_id)
        self.assertEqual(sec1_info["percentage"], 100.0)
        self.assertTrue(sec1_info["is_complete"])

        sec2_info = next(s for s in prog["sections"] if s["section_id"] == s2_id)
        self.assertEqual(sec2_info["percentage"], 0.0)
        self.assertFalse(sec2_info["is_complete"])

    def test_progress_nonexistent_resources_raise_404(self) -> None:
        j_resp = self.client.get("/journeys/99999/progress")
        self.assertEqual(j_resp.status_code, 404)

        s_resp = self.client.get("/sections/99999/progress")
        self.assertEqual(s_resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
