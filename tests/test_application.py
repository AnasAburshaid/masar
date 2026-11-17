"""Tests for application services and use cases."""

import unittest

from masar.application.services import JourneyService
from masar.domain.exceptions import JourneyNotFoundError, ValidationError
from masar.infrastructure.repositories import InMemoryJourneyRepository


class TestJourneyService(unittest.TestCase):
    """Test suite for JourneyService."""

    def setUp(self) -> None:
        self.repo = InMemoryJourneyRepository()
        self.service = JourneyService(self.repo)

    def test_create_journey_success(self) -> None:
        journey = self.service.create_journey(title="FastAPI", description="Build APIs")
        self.assertEqual(journey.id, 1)
        self.assertEqual(journey.title, "FastAPI")
        self.assertEqual(journey.description, "Build APIs")

    def test_create_journey_empty_title_fails(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_journey(title="   ")

    def test_list_journeys(self) -> None:
        self.assertEqual(self.service.list_journeys(), [])
        self.service.create_journey(title="J1")
        self.service.create_journey(title="J2")
        self.assertEqual(len(self.service.list_journeys()), 2)

    def test_get_journey_success_and_not_found(self) -> None:
        created = self.service.create_journey(title="Testing")
        found = self.service.get_journey(created.id)
        self.assertEqual(found.title, "Testing")

        with self.assertRaises(JourneyNotFoundError):
            self.service.get_journey(999)

    def test_update_journey_success(self) -> None:
        created = self.service.create_journey(title="Initial", description="Desc")
        updated = self.service.update_journey(created.id, title="Updated", description="New Desc")
        self.assertEqual(updated.title, "Updated")
        self.assertEqual(updated.description, "New Desc")

    def test_update_journey_not_found(self) -> None:
        with self.assertRaises(JourneyNotFoundError):
            self.service.update_journey(999, title="Whatever")

    def test_delete_journey_success_and_not_found(self) -> None:
        created = self.service.create_journey(title="To Remove")
        self.service.delete_journey(created.id)
        with self.assertRaises(JourneyNotFoundError):
            self.service.get_journey(created.id)

        with self.assertRaises(JourneyNotFoundError):
            self.service.delete_journey(999)


if __name__ == "__main__":
    unittest.main()
