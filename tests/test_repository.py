"""Tests for repository implementations."""

import unittest

from masar.domain.exceptions import JourneyNotFoundError
from masar.domain.models import Journey
from masar.infrastructure.repositories import InMemoryJourneyRepository


class TestInMemoryJourneyRepository(unittest.TestCase):
    """Test suite for InMemoryJourneyRepository."""

    def setUp(self) -> None:
        self.repo = InMemoryJourneyRepository()

    def test_add_assigns_auto_incrementing_ids(self) -> None:
        j1 = self.repo.add(Journey(title="Journey 1"))
        j2 = self.repo.add(Journey(title="Journey 2"))
        self.assertEqual(j1.id, 1)
        self.assertEqual(j2.id, 2)

    def test_get_by_id_found_and_not_found(self) -> None:
        created = self.repo.add(Journey(title="Python"))
        found = self.repo.get_by_id(created.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Python")

        missing = self.repo.get_by_id(999)
        self.assertIsNone(missing)

    def test_get_all_returns_all_journeys(self) -> None:
        self.assertEqual(self.repo.get_all(), [])
        self.repo.add(Journey(title="First"))
        self.repo.add(Journey(title="Second"))
        journeys = self.repo.get_all()
        self.assertEqual(len(journeys), 2)
        self.assertEqual([j.title for j in journeys], ["First", "Second"])

    def test_update_existing_journey(self) -> None:
        j = self.repo.add(Journey(title="Old Title"))
        j.title = "New Title"
        updated = self.repo.update(j)
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(self.repo.get_by_id(j.id).title, "New Title")

    def test_update_non_existing_journey_raises_error(self) -> None:
        fake = Journey(title="Fake", id=999)
        with self.assertRaises(JourneyNotFoundError):
            self.repo.update(fake)

    def test_delete_existing_and_non_existing(self) -> None:
        j = self.repo.add(Journey(title="To Delete"))
        self.assertTrue(self.repo.delete(j.id))
        self.assertIsNone(self.repo.get_by_id(j.id))
        self.assertFalse(self.repo.delete(j.id))


if __name__ == "__main__":
    unittest.main()
