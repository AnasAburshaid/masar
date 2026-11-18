"""Tests for repository implementations."""

import unittest

from masar.domain.exceptions import (
    JourneyNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Journey, Section, Topic
from masar.infrastructure.repositories import (
    InMemoryJourneyRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)


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


class TestInMemorySectionRepository(unittest.TestCase):
    """Test suite for InMemorySectionRepository."""

    def setUp(self) -> None:
        self.repo = InMemorySectionRepository()

    def test_add_and_get_by_id(self) -> None:
        s1 = self.repo.add(Section(journey_id=1, title="Basics"))
        self.assertEqual(s1.id, 1)
        self.assertEqual(self.repo.get_by_id(1).title, "Basics")
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_journey_id(self) -> None:
        self.repo.add(Section(journey_id=1, title="S1"))
        self.repo.add(Section(journey_id=1, title="S2"))
        self.repo.add(Section(journey_id=2, title="Other Journey S"))

        j1_sections = self.repo.get_by_journey_id(1)
        self.assertEqual(len(j1_sections), 2)
        self.assertEqual([s.title for s in j1_sections], ["S1", "S2"])

    def test_update_section(self) -> None:
        s = self.repo.add(Section(journey_id=1, title="Initial"))
        s.title = "Updated"
        updated = self.repo.update(s)
        self.assertEqual(updated.title, "Updated")

        missing = Section(journey_id=1, title="Ghost", id=999)
        with self.assertRaises(SectionNotFoundError):
            self.repo.update(missing)

    def test_delete_section(self) -> None:
        s = self.repo.add(Section(journey_id=1, title="To Delete"))
        self.assertTrue(self.repo.delete(s.id))
        self.assertFalse(self.repo.delete(s.id))

    def test_delete_by_journey_id(self) -> None:
        self.repo.add(Section(journey_id=1, title="S1"))
        self.repo.add(Section(journey_id=1, title="S2"))
        self.repo.add(Section(journey_id=2, title="S3"))

        count = self.repo.delete_by_journey_id(1)
        self.assertEqual(count, 2)
        self.assertEqual(len(self.repo.get_by_journey_id(1)), 0)
        self.assertEqual(len(self.repo.get_by_journey_id(2)), 1)


class TestInMemoryTopicRepository(unittest.TestCase):
    """Test suite for InMemoryTopicRepository."""

    def setUp(self) -> None:
        self.repo = InMemoryTopicRepository()

    def test_add_and_get_by_id(self) -> None:
        t1 = self.repo.add(Topic(section_id=10, title="Variables"))
        self.assertEqual(t1.id, 1)
        self.assertEqual(self.repo.get_by_id(1).title, "Variables")
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_section_id(self) -> None:
        self.repo.add(Topic(section_id=1, title="T1"))
        self.repo.add(Topic(section_id=1, title="T2"))
        self.repo.add(Topic(section_id=2, title="T3"))

        s1_topics = self.repo.get_by_section_id(1)
        self.assertEqual(len(s1_topics), 2)
        self.assertEqual([t.title for t in s1_topics], ["T1", "T2"])

    def test_update_topic(self) -> None:
        t = self.repo.add(Topic(section_id=1, title="Variables"))
        t.title = "Variables & Memory"
        t.mark_completed()
        updated = self.repo.update(t)
        self.assertEqual(updated.title, "Variables & Memory")
        self.assertTrue(updated.is_completed)

        fake = Topic(section_id=1, title="Ghost", id=999)
        with self.assertRaises(TopicNotFoundError):
            self.repo.update(fake)

    def test_delete_topic(self) -> None:
        t = self.repo.add(Topic(section_id=1, title="Delete Me"))
        self.assertTrue(self.repo.delete(t.id))
        self.assertFalse(self.repo.delete(t.id))

    def test_delete_by_section_id(self) -> None:
        self.repo.add(Topic(section_id=1, title="T1"))
        self.repo.add(Topic(section_id=1, title="T2"))
        self.repo.add(Topic(section_id=2, title="T3"))

        count = self.repo.delete_by_section_id(1)
        self.assertEqual(count, 2)
        self.assertEqual(len(self.repo.get_by_section_id(1)), 0)
        self.assertEqual(len(self.repo.get_by_section_id(2)), 1)


if __name__ == "__main__":
    unittest.main()
