"""Integration tests for Sections, Topics, and Notes REST API endpoints."""

import unittest

from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.presentation.api.app import create_app


class TestSectionsTopicsNotesAPI(unittest.TestCase):
    """Test suite for Sections, Topics, and Notes API endpoints."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            environment="testing",
        )
        self.app = create_app(settings=self.settings)
        self.client = TestClient(self.app)

        # Create a base journey for relationship testing
        journey_resp = self.client.post("/journeys", json={"title": "Backend Track", "description": "Python"})
        self.assertEqual(journey_resp.status_code, 201)
        self.journey_id = journey_resp.json()["id"]

    # ==================== SECTIONS TESTS ====================

    def test_create_section_success(self) -> None:
        response = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "FastAPI Basics"})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "FastAPI Basics")
        self.assertEqual(data["journey_id"], self.journey_id)
        self.assertGreater(data["id"], 0)

    def test_create_section_nonexistent_journey_raises_404(self) -> None:
        response = self.client.post("/sections", json={"journey_id": 99999, "title": "Orphan Section"})
        self.assertEqual(response.status_code, 404)

    def test_create_section_empty_title_raises_422(self) -> None:
        response = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "   "})
        self.assertEqual(response.status_code, 422)

    def test_get_section_success_and_not_found(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Architecture"}).json()
        sec_id = sec["id"]

        get_resp = self.client.get(f"/sections/{sec_id}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["title"], "Architecture")

        nf_resp = self.client.get("/sections/99999")
        self.assertEqual(nf_resp.status_code, 404)

    def test_list_sections_routes(self) -> None:
        self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Part 1"})
        self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Part 2"})

        # Test nested route
        resp1 = self.client.get(f"/journeys/{self.journey_id}/sections")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.json()), 2)

        # Test query param route
        resp2 = self.client.get(f"/sections?journey_id={self.journey_id}")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.json()), 2)

    def test_list_sections_nonexistent_journey_raises_404(self) -> None:
        response = self.client.get("/journeys/99999/sections")
        self.assertEqual(response.status_code, 404)

    def test_update_section(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Old Name"}).json()
        sec_id = sec["id"]

        update_resp = self.client.patch(f"/sections/{sec_id}", json={"title": "New Name"})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["title"], "New Name")

    def test_delete_section_success_and_not_found(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Delete Me"}).json()
        sec_id = sec["id"]

        del_resp = self.client.delete(f"/sections/{sec_id}")
        self.assertEqual(del_resp.status_code, 204)

        del_again = self.client.delete(f"/sections/{sec_id}")
        self.assertEqual(del_again.status_code, 404)

    # ==================== TOPICS TESTS ====================

    def test_create_topic_success(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section A"}).json()
        sec_id = sec["id"]

        response = self.client.post("/topics", json={"section_id": sec_id, "title": "Routing", "is_completed": True})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Routing")
        self.assertEqual(data["section_id"], sec_id)
        self.assertTrue(data["is_completed"])

    def test_create_topic_nonexistent_section_raises_404(self) -> None:
        response = self.client.post("/topics", json={"section_id": 99999, "title": "Orphan Topic"})
        self.assertEqual(response.status_code, 404)

    def test_get_topic_success_and_not_found(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section B"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Middleware"}).json()
        top_id = top["id"]

        resp = self.client.get(f"/topics/{top_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "Middleware")

        nf = self.client.get("/topics/99999")
        self.assertEqual(nf.status_code, 404)

    def test_list_topics_routes(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section C"}).json()
        sec_id = sec["id"]

        self.client.post("/topics", json={"section_id": sec_id, "title": "Topic 1"})
        self.client.post("/topics", json={"section_id": sec_id, "title": "Topic 2"})

        resp1 = self.client.get(f"/sections/{sec_id}/topics")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.json()), 2)

        resp2 = self.client.get(f"/topics?section_id={sec_id}")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.json()), 2)

    def test_update_topic_and_status_endpoints(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section D"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Initial Topic"}).json()
        top_id = top["id"]
        self.assertFalse(top["is_completed"])

        # Mark completed via dedicated endpoint
        comp_resp = self.client.patch(f"/topics/{top_id}/complete")
        self.assertEqual(comp_resp.status_code, 200)
        self.assertTrue(comp_resp.json()["is_completed"])

        # Mark pending via dedicated endpoint
        pend_resp = self.client.patch(f"/topics/{top_id}/pending")
        self.assertEqual(pend_resp.status_code, 200)
        self.assertFalse(pend_resp.json()["is_completed"])

        # Update title & status via patch
        patch_resp = self.client.patch(f"/topics/{top_id}", json={"title": "Renamed Topic", "is_completed": True})
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.json()["title"], "Renamed Topic")
        self.assertTrue(patch_resp.json()["is_completed"])

    def test_delete_topic_success_and_not_found(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section E"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "To Delete"}).json()
        top_id = top["id"]

        del_resp = self.client.delete(f"/topics/{top_id}")
        self.assertEqual(del_resp.status_code, 204)

        del_again = self.client.delete(f"/topics/{top_id}")
        self.assertEqual(del_again.status_code, 404)

    # ==================== NOTES TESTS ====================

    def test_create_note_success(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section F"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Topic with note"}).json()
        top_id = top["id"]

        resp = self.client.post("/notes", json={"topic_id": top_id, "content": "Remember to write tests"})
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["content"], "Remember to write tests")
        self.assertEqual(data["topic_id"], top_id)
        self.assertGreater(data["id"], 0)

    def test_create_note_nonexistent_topic_raises_404(self) -> None:
        resp = self.client.post("/notes", json={"topic_id": 99999, "content": "Orphan note"})
        self.assertEqual(resp.status_code, 404)

    def test_create_note_empty_content_raises_422(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section G"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Topic"}).json()

        resp = self.client.post("/notes", json={"topic_id": top["id"], "content": "   "})
        self.assertEqual(resp.status_code, 422)

    def test_get_and_list_notes(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section H"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Topic with notes"}).json()
        top_id = top["id"]

        n1 = self.client.post("/notes", json={"topic_id": top_id, "content": "Note 1"}).json()
        self.client.post("/notes", json={"topic_id": top_id, "content": "Note 2"})

        get_resp = self.client.get(f"/notes/{n1['id']}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["content"], "Note 1")

        list1 = self.client.get(f"/topics/{top_id}/notes")
        self.assertEqual(list1.status_code, 200)
        self.assertEqual(len(list1.json()), 2)

        list2 = self.client.get(f"/notes?topic_id={top_id}")
        self.assertEqual(list2.status_code, 200)
        self.assertEqual(len(list2.json()), 2)

    def test_update_and_delete_note(self) -> None:
        sec = self.client.post("/sections", json={"journey_id": self.journey_id, "title": "Section I"}).json()
        top = self.client.post("/topics", json={"section_id": sec["id"], "title": "Topic"}).json()
        note = self.client.post("/notes", json={"topic_id": top["id"], "content": "Old Content"}).json()
        note_id = note["id"]

        update_resp = self.client.put(f"/notes/{note_id}", json={"content": "Updated Content"})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["content"], "Updated Content")

        del_resp = self.client.delete(f"/notes/{note_id}")
        self.assertEqual(del_resp.status_code, 204)

        del_again = self.client.delete(f"/notes/{note_id}")
        self.assertEqual(del_again.status_code, 404)


if __name__ == "__main__":
    unittest.main()
