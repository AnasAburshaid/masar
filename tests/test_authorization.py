"""Unit and integration tests for User Authorization and Data Ownership (Issue #33)."""

import unittest

from fastapi.testclient import TestClient

from masar.config.settings import Settings
from masar.domain.exceptions import AccessDeniedError, InvalidIdError
from masar.domain.models import Journey
from masar.presentation.api.app import create_app


class TestJourneyDomainOwnership(unittest.TestCase):
    """Test user_id validation on Journey domain model."""

    def test_journey_with_valid_user_id(self) -> None:
        journey = Journey(title="Architecture Track", user_id=10)
        self.assertEqual(journey.user_id, 10)

    def test_journey_with_invalid_user_id_raises_invalid_id_error(self) -> None:
        with self.assertRaises(InvalidIdError):
            Journey(title="Bad User ID", user_id=0)
        with self.assertRaises(InvalidIdError):
            Journey(title="Negative User ID", user_id=-1)


class TestUnauthenticatedAccessRestriction(unittest.TestCase):
    """Verify that unauthenticated requests to protected endpoints return 401 Unauthorized."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            environment="production",  # Production environment enforces authentication strictly
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

    def test_endpoints_reject_unauthenticated_requests(self) -> None:
        protected_routes = [
            ("GET", "/journeys"),
            ("POST", "/journeys"),
            ("GET", "/journeys/1"),
            ("PUT", "/journeys/1"),
            ("DELETE", "/journeys/1"),
            ("POST", "/sections"),
            ("GET", "/sections/1"),
            ("GET", "/journeys/1/sections"),
            ("PUT", "/sections/1"),
            ("DELETE", "/sections/1"),
            ("POST", "/topics"),
            ("GET", "/topics/1"),
            ("GET", "/sections/1/topics"),
            ("PATCH", "/topics/1"),
            ("DELETE", "/topics/1"),
            ("POST", "/notes"),
            ("GET", "/notes/1"),
            ("GET", "/topics/1/notes"),
            ("PUT", "/notes/1"),
            ("DELETE", "/notes/1"),
            ("GET", "/journeys/1/progress"),
            ("GET", "/sections/1/progress"),
        ]

        for method, route in protected_routes:
            with self.subTest(method=method, route=route):
                if method == "GET":
                    resp = self.client.get(route)
                elif method == "POST":
                    resp = self.client.post(route, json={})
                elif method == "PUT":
                    resp = self.client.put(route, json={})
                elif method == "PATCH":
                    resp = self.client.patch(route, json={})
                elif method == "DELETE":
                    resp = self.client.delete(route)
                else:
                    continue

                self.assertEqual(
                    resp.status_code,
                    401,
                    f"Route {method} {route} should reject unauthenticated request with 401, got {resp.status_code}",
                )
                self.assertEqual(resp.headers.get("www-authenticate"), "Bearer")


class TestMultiUserDataOwnershipAndIsolation(unittest.TestCase):
    """Test cross-user isolation across journeys, sections, topics, notes, and progress."""

    def setUp(self) -> None:
        self.settings = Settings(
            storage_type="in_memory",
            strict_auth=True,
            jwt_secret_key="secret-key-that-is-at-least-32-bytes-long",
        )
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)

        # Register User A
        res_a = self.client.post(
            "/auth/register",
            json={"email": "usera@example.com", "password": "Password123!"},
        )
        self.assertEqual(res_a.status_code, 201)
        login_a = self.client.post(
            "/auth/login",
            json={"email": "usera@example.com", "password": "Password123!"},
        )
        self.token_a = login_a.json()["access_token"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Register User B
        res_b = self.client.post(
            "/auth/register",
            json={"email": "userb@example.com", "password": "Password123!"},
        )
        self.assertEqual(res_b.status_code, 201)
        login_b = self.client.post(
            "/auth/login",
            json={"email": "userb@example.com", "password": "Password123!"},
        )
        self.token_b = login_b.json()["access_token"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

        # User A creates a complete hierarchy: Journey A -> Section A -> Topic A -> Note A
        j_resp = self.client.post(
            "/journeys",
            json={"title": "User A Journey", "description": "Private track"},
            headers=self.headers_a,
        )
        self.assertEqual(j_resp.status_code, 201)
        self.journey_a_id = j_resp.json()["id"]

        s_resp = self.client.post(
            "/sections",
            json={"journey_id": self.journey_a_id, "title": "User A Section"},
            headers=self.headers_a,
        )
        self.assertEqual(s_resp.status_code, 201)
        self.section_a_id = s_resp.json()["id"]

        t_resp = self.client.post(
            "/topics",
            json={"section_id": self.section_a_id, "title": "User A Topic"},
            headers=self.headers_a,
        )
        self.assertEqual(t_resp.status_code, 201)
        self.topic_a_id = t_resp.json()["id"]

        n_resp = self.client.post(
            "/notes",
            json={"topic_id": self.topic_a_id, "content": "User A Secret Note"},
            headers=self.headers_a,
        )
        self.assertEqual(n_resp.status_code, 201)
        self.note_a_id = n_resp.json()["id"]

    def test_user_b_cannot_see_user_a_journey_in_list(self) -> None:
        # User A sees 1 journey
        resp_a = self.client.get("/journeys", headers=self.headers_a)
        self.assertEqual(len(resp_a.json()), 1)
        self.assertEqual(resp_a.json()[0]["id"], self.journey_a_id)

        # User B sees 0 journeys
        resp_b = self.client.get("/journeys", headers=self.headers_b)
        self.assertEqual(len(resp_b.json()), 0)

    def test_user_b_cannot_access_or_modify_user_a_journey(self) -> None:
        # Read
        get_resp = self.client.get(f"/journeys/{self.journey_a_id}", headers=self.headers_b)
        self.assertEqual(get_resp.status_code, 403)

        # Update
        put_resp = self.client.put(
            f"/journeys/{self.journey_a_id}",
            json={"title": "Hacked Title"},
            headers=self.headers_b,
        )
        self.assertEqual(put_resp.status_code, 403)

        # Delete
        del_resp = self.client.delete(f"/journeys/{self.journey_a_id}", headers=self.headers_b)
        self.assertEqual(del_resp.status_code, 403)

    def test_user_b_cannot_access_or_modify_user_a_section(self) -> None:
        # Create section in User A's journey
        post_resp = self.client.post(
            "/sections",
            json={"journey_id": self.journey_a_id, "title": "Injected Section"},
            headers=self.headers_b,
        )
        self.assertEqual(post_resp.status_code, 403)

        # Read section
        get_resp = self.client.get(f"/sections/{self.section_a_id}", headers=self.headers_b)
        self.assertEqual(get_resp.status_code, 403)

        # List sections for User A's journey
        list_resp = self.client.get(f"/journeys/{self.journey_a_id}/sections", headers=self.headers_b)
        self.assertEqual(list_resp.status_code, 403)

        # Update section
        put_resp = self.client.put(
            f"/sections/{self.section_a_id}",
            json={"title": "Renamed Section"},
            headers=self.headers_b,
        )
        self.assertEqual(put_resp.status_code, 403)

        # Delete section
        del_resp = self.client.delete(f"/sections/{self.section_a_id}", headers=self.headers_b)
        self.assertEqual(del_resp.status_code, 403)

    def test_user_b_cannot_access_or_modify_user_a_topic(self) -> None:
        # Create topic in User A's section
        post_resp = self.client.post(
            "/topics",
            json={"section_id": self.section_a_id, "title": "Injected Topic"},
            headers=self.headers_b,
        )
        self.assertEqual(post_resp.status_code, 403)

        # Read topic
        get_resp = self.client.get(f"/topics/{self.topic_a_id}", headers=self.headers_b)
        self.assertEqual(get_resp.status_code, 403)

        # List topics in User A's section
        list_resp = self.client.get(f"/sections/{self.section_a_id}/topics", headers=self.headers_b)
        self.assertEqual(list_resp.status_code, 403)

        # Update topic
        put_resp = self.client.patch(
            f"/topics/{self.topic_a_id}",
            json={"title": "Hacked Topic"},
            headers=self.headers_b,
        )
        self.assertEqual(put_resp.status_code, 403)

        # Mark completed
        comp_resp = self.client.patch(f"/topics/{self.topic_a_id}/complete", headers=self.headers_b)
        self.assertEqual(comp_resp.status_code, 403)

        # Delete topic
        del_resp = self.client.delete(f"/topics/{self.topic_a_id}", headers=self.headers_b)
        self.assertEqual(del_resp.status_code, 403)

    def test_user_b_cannot_access_or_modify_user_a_note(self) -> None:
        # Create note in User A's topic
        post_resp = self.client.post(
            "/notes",
            json={"topic_id": self.topic_a_id, "content": "Injected Note"},
            headers=self.headers_b,
        )
        self.assertEqual(post_resp.status_code, 403)

        # Read note
        get_resp = self.client.get(f"/notes/{self.note_a_id}", headers=self.headers_b)
        self.assertEqual(get_resp.status_code, 403)

        # List notes in User A's topic
        list_resp = self.client.get(f"/topics/{self.topic_a_id}/notes", headers=self.headers_b)
        self.assertEqual(list_resp.status_code, 403)

        # Update note
        put_resp = self.client.put(
            f"/notes/{self.note_a_id}",
            json={"content": "Overwritten Note"},
            headers=self.headers_b,
        )
        self.assertEqual(put_resp.status_code, 403)

        # Delete note
        del_resp = self.client.delete(f"/notes/{self.note_a_id}", headers=self.headers_b)
        self.assertEqual(del_resp.status_code, 403)

    def test_user_b_cannot_view_user_a_progress(self) -> None:
        # Journey progress
        j_prog = self.client.get(f"/journeys/{self.journey_a_id}/progress", headers=self.headers_b)
        self.assertEqual(j_prog.status_code, 403)

        # Section progress
        s_prog = self.client.get(f"/sections/{self.section_a_id}/progress", headers=self.headers_b)
        self.assertEqual(s_prog.status_code, 403)


class TestMultiUserDatabaseStorage(unittest.TestCase):
    """Test user isolation with SQL database persistence."""

    def test_database_persistence_multi_user(self) -> None:
        settings = Settings(
            storage_type="database",
            database_url="sqlite://",
            strict_auth=True,
            jwt_secret_key="database-test-secret-at-least-32-bytes-long",
        )
        app = create_app(settings)
        client = TestClient(app)

        # Register and log in User 1
        client.post("/auth/register", json={"email": "db1@masar.dev", "password": "Password123!"})
        t1 = client.post("/auth/login", json={"email": "db1@masar.dev", "password": "Password123!"}).json()["access_token"]
        h1 = {"Authorization": f"Bearer {t1}"}

        # Register and log in User 2
        client.post("/auth/register", json={"email": "db2@masar.dev", "password": "Password123!"})
        t2 = client.post("/auth/login", json={"email": "db2@masar.dev", "password": "Password123!"}).json()["access_token"]
        h2 = {"Authorization": f"Bearer {t2}"}

        # User 1 creates a journey
        j1_resp = client.post("/journeys", json={"title": "DB1 Journey"}, headers=h1)
        self.assertEqual(j1_resp.status_code, 201)
        j1_id = j1_resp.json()["id"]

        # User 2 creates a journey
        j2_resp = client.post("/journeys", json={"title": "DB2 Journey"}, headers=h2)
        self.assertEqual(j2_resp.status_code, 201)
        j2_id = j2_resp.json()["id"]

        # User 1 lists: only sees Journey 1
        j1_list = client.get("/journeys", headers=h1).json()
        self.assertEqual([j["id"] for j in j1_list], [j1_id])

        # User 2 lists: only sees Journey 2
        j2_list = client.get("/journeys", headers=h2).json()
        self.assertEqual([j["id"] for j in j2_list], [j2_id])

        # Cross-access is forbidden
        self.assertEqual(client.get(f"/journeys/{j1_id}", headers=h2).status_code, 403)
        self.assertEqual(client.get(f"/journeys/{j2_id}", headers=h1).status_code, 403)
