"""Integration tests for Learning Journey REST API endpoints."""

import unittest

from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestJourneyAPI(unittest.TestCase):
    """Test suite for /journeys API endpoints."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            environment="testing",
        )
        self.app = create_app(settings=self.settings)
        self.client = TestClient(self.app)

    # ---------------- POST /journeys ----------------

    def test_create_journey_success(self) -> None:
        payload = {"title": "FastAPI Mastery", "description": "From beginner to pro"}
        response = self.client.post("/journeys", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "FastAPI Mastery")
        self.assertEqual(data["description"], "From beginner to pro")
        self.assertGreater(data["id"], 0)
        self.assertIn("created_at", data)

    def test_create_journey_empty_title_fails(self) -> None:
        response = self.client.post("/journeys", json={"title": "   ", "description": "desc"})
        self.assertEqual(response.status_code, 422)

    def test_create_journey_title_too_long_fails(self) -> None:
        response = self.client.post("/journeys", json={"title": "a" * 101})
        self.assertEqual(response.status_code, 422)

    # ---------------- GET /journeys ----------------

    def test_list_journeys_empty_and_populated(self) -> None:
        # Initially empty
        response = self.client.get("/journeys")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # Add two journeys
        self.client.post("/journeys", json={"title": "Python Basics"})
        self.client.post("/journeys", json={"title": "Clean Architecture"})

        response = self.client.get("/journeys")
        self.assertEqual(response.status_code, 200)
        journeys = response.json()
        self.assertEqual(len(journeys), 2)
        titles = [j["title"] for j in journeys]
        self.assertIn("Python Basics", titles)
        self.assertIn("Clean Architecture", titles)

    # ---------------- GET /journeys/{id} ----------------

    def test_get_journey_by_id_success(self) -> None:
        created = self.client.post("/journeys", json={"title": "Django Deep Dive"}).json()
        journey_id = created["id"]

        response = self.client.get(f"/journeys/{journey_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], journey_id)
        self.assertEqual(data["title"], "Django Deep Dive")

    def test_get_journey_not_found(self) -> None:
        response = self.client.get("/journeys/9999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_get_journey_invalid_id_fails_validation(self) -> None:
        response = self.client.get("/journeys/0")
        self.assertEqual(response.status_code, 422)

        response_negative = self.client.get("/journeys/-5")
        self.assertEqual(response_negative.status_code, 422)

    # ---------------- PUT / PATCH /journeys/{id} ----------------

    def test_update_journey_put_full(self) -> None:
        created = self.client.post("/journeys", json={"title": "Initial", "description": "Init desc"}).json()
        journey_id = created["id"]

        response = self.client.put(
            f"/journeys/{journey_id}",
            json={"title": "Updated Title", "description": "Updated Description"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Updated Title")
        self.assertEqual(data["description"], "Updated Description")

    def test_update_journey_patch_partial(self) -> None:
        created = self.client.post("/journeys", json={"title": "Original Title", "description": "Keep this"}).json()
        journey_id = created["id"]

        # Patch only title
        response = self.client.patch(
            f"/journeys/{journey_id}",
            json={"title": "New Title Only"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "New Title Only")
        self.assertEqual(data["description"], "Keep this")

    def test_update_journey_not_found(self) -> None:
        response = self.client.put("/journeys/8888", json={"title": "Won't Work"})
        self.assertEqual(response.status_code, 404)

    # ---------------- DELETE /journeys/{id} ----------------

    def test_delete_journey_success_and_cascade(self) -> None:
        created = self.client.post("/journeys", json={"title": "To Delete"}).json()
        journey_id = created["id"]

        # Delete journey
        delete_resp = self.client.delete(f"/journeys/{journey_id}")
        self.assertEqual(delete_resp.status_code, 204)

        # Subsequent GET should return 404
        get_resp = self.client.get(f"/journeys/{journey_id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_journey_not_found(self) -> None:
        response = self.client.delete("/journeys/7777")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
