"""Tests for FastAPI initialization, root, and health endpoints."""

import unittest

from fastapi.testclient import TestClient

from masar.application.services import JourneyService
from masar.config.settings import Settings
from masar.container import build_container
from masar.presentation.api.app import create_app
from masar.presentation.api.dependencies import (
    get_journey_service,
    get_note_service,
    get_progress_service,
    get_section_service,
    get_topic_service,
)


class TestFastAPIInitialization(unittest.TestCase):
    """Test suite for FastAPI application initialization."""

    def setUp(self) -> None:
        self.settings = Settings(
            app_name="Masar Test API",
            storage_type="in_memory",
            environment="testing",
        )
        self.app = create_app(settings=self.settings)
        self.client = TestClient(self.app)

    def test_root_endpoint_returns_metadata(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Welcome to Masar API")
        self.assertEqual(data["app_name"], "Masar Test API")
        self.assertEqual(data["environment"], "testing")
        self.assertEqual(data["docs_url"], "/docs")
        self.assertEqual(data["health_url"], "/health")

    def test_health_check_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["environment"], "testing")
        self.assertEqual(data["storage_type"], "in_memory")

    def test_openapi_documentation_accessible(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["info"]["title"], "Masar Test API")
        self.assertEqual(schema["info"]["version"], "0.1.0")

        docs_response = self.client.get("/docs")
        self.assertEqual(docs_response.status_code, 200)

    def test_dependencies_resolve_services(self) -> None:
        services = build_container(settings=self.settings)
        self.assertEqual(len(services), 5)
        journey_svc = get_journey_service(services=services)
        self.assertIsInstance(journey_svc, JourneyService)
        self.assertIsNotNone(get_section_service(services=services))
        self.assertIsNotNone(get_topic_service(services=services))
        self.assertIsNotNone(get_note_service(services=services))
        self.assertIsNotNone(get_progress_service(services=services))


if __name__ == "__main__":
    unittest.main()
