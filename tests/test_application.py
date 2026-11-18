"""Tests for application services and use cases."""

import unittest

from masar.application.services import JourneyService, SectionService, TopicService
from masar.domain.exceptions import (
    JourneyNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
    ValidationError,
)
from masar.domain.models import Section, Topic
from masar.infrastructure.repositories import (
    InMemoryJourneyRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)


class TestJourneyService(unittest.TestCase):
    """Test suite for JourneyService."""

    def setUp(self) -> None:
        self.journey_repo = InMemoryJourneyRepository()
        self.section_repo = InMemorySectionRepository()
        self.topic_repo = InMemoryTopicRepository()
        self.service = JourneyService(
            repository=self.journey_repo,
            section_repository=self.section_repo,
            topic_repository=self.topic_repo,
        )

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

    def test_delete_journey_cascades_to_sections_and_topics(self) -> None:
        journey = self.service.create_journey(title="Full Stack")
        section_service = SectionService(self.section_repo, self.journey_repo, self.topic_repo)
        sec = section_service.create_section(journey.id, "Frontend")
        topic_service = TopicService(self.topic_repo, self.section_repo)
        top = topic_service.create_topic(sec.id, "React")

        self.service.delete_journey(journey.id)

        self.assertEqual(len(self.section_repo.get_by_journey_id(journey.id)), 0)
        self.assertEqual(len(self.topic_repo.get_by_section_id(sec.id)), 0)


class TestSectionService(unittest.TestCase):
    """Test suite for SectionService."""

    def setUp(self) -> None:
        self.journey_repo = InMemoryJourneyRepository()
        self.section_repo = InMemorySectionRepository()
        self.topic_repo = InMemoryTopicRepository()
        self.journey_service = JourneyService(self.journey_repo)
        self.section_service = SectionService(
            section_repository=self.section_repo,
            journey_repository=self.journey_repo,
            topic_repository=self.topic_repo,
        )
        self.journey = self.journey_service.create_journey("Python Basics")

    def test_create_section_valid(self) -> None:
        sec = self.section_service.create_section(self.journey.id, "Fundamentals")
        self.assertEqual(sec.id, 1)
        self.assertEqual(sec.journey_id, self.journey.id)
        self.assertEqual(sec.title, "Fundamentals")

    def test_create_section_nonexistent_journey(self) -> None:
        with self.assertRaises(JourneyNotFoundError):
            self.section_service.create_section(999, "Invalid Journey Section")

    def test_create_section_empty_title(self) -> None:
        with self.assertRaises(ValidationError):
            self.section_service.create_section(self.journey.id, "   ")

    def test_list_sections(self) -> None:
        self.section_service.create_section(self.journey.id, "S1")
        self.section_service.create_section(self.journey.id, "S2")
        sections = self.section_service.list_sections(self.journey.id)
        self.assertEqual(len(sections), 2)
        self.assertEqual([s.title for s in sections], ["S1", "S2"])

    def test_list_sections_nonexistent_journey(self) -> None:
        with self.assertRaises(JourneyNotFoundError):
            self.section_service.list_sections(999)

    def test_get_section_success_and_not_found(self) -> None:
        sec = self.section_service.create_section(self.journey.id, "OOP")
        found = self.section_service.get_section(sec.id)
        self.assertEqual(found.title, "OOP")

        with self.assertRaises(SectionNotFoundError):
            self.section_service.get_section(999)

    def test_rename_section(self) -> None:
        sec = self.section_service.create_section(self.journey.id, "OOP")
        renamed = self.section_service.rename_section(sec.id, "Advanced OOP")
        self.assertEqual(renamed.title, "Advanced OOP")

        with self.assertRaises(ValidationError):
            self.section_service.rename_section(sec.id, "")

        with self.assertRaises(SectionNotFoundError):
            self.section_service.rename_section(999, "Does Not Exist")

    def test_delete_section_and_cascades_topics(self) -> None:
        sec = self.section_service.create_section(self.journey.id, "Data Structures")
        topic_service = TopicService(self.topic_repo, self.section_repo)
        topic_service.create_topic(sec.id, "Lists")
        topic_service.create_topic(sec.id, "Dictionaries")

        self.section_service.delete_section(sec.id)

        with self.assertRaises(SectionNotFoundError):
            self.section_service.get_section(sec.id)

        self.assertEqual(len(self.topic_repo.get_by_section_id(sec.id)), 0)

        with self.assertRaises(SectionNotFoundError):
            self.section_service.delete_section(999)


class TestTopicService(unittest.TestCase):
    """Test suite for TopicService."""

    def setUp(self) -> None:
        self.section_repo = InMemorySectionRepository()
        self.topic_repo = InMemoryTopicRepository()
        self.section = self.section_repo.add(Section(journey_id=1, title="Core"))
        self.service = TopicService(self.topic_repo, self.section_repo)

    def test_create_topic_valid(self) -> None:
        t = self.service.create_topic(self.section.id, "Variables")
        self.assertEqual(t.id, 1)
        self.assertEqual(t.section_id, self.section.id)
        self.assertEqual(t.title, "Variables")
        self.assertFalse(t.is_completed)

    def test_create_topic_nonexistent_section(self) -> None:
        with self.assertRaises(SectionNotFoundError):
            self.service.create_topic(999, "Orphan Topic")

    def test_create_topic_empty_title(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_topic(self.section.id, "   ")

    def test_list_topics(self) -> None:
        self.service.create_topic(self.section.id, "T1")
        self.service.create_topic(self.section.id, "T2")
        topics = self.service.list_topics(self.section.id)
        self.assertEqual(len(topics), 2)
        self.assertEqual([t.title for t in topics], ["T1", "T2"])

    def test_list_topics_nonexistent_section(self) -> None:
        with self.assertRaises(SectionNotFoundError):
            self.service.list_topics(999)

    def test_get_topic_success_and_not_found(self) -> None:
        t = self.service.create_topic(self.section.id, "Loops")
        found = self.service.get_topic(t.id)
        self.assertEqual(found.title, "Loops")

        with self.assertRaises(TopicNotFoundError):
            self.service.get_topic(999)

    def test_rename_topic(self) -> None:
        t = self.service.create_topic(self.section.id, "Loops")
        renamed = self.service.rename_topic(t.id, "While and For Loops")
        self.assertEqual(renamed.title, "While and For Loops")

        with self.assertRaises(ValidationError):
            self.service.rename_topic(t.id, "  ")

        with self.assertRaises(TopicNotFoundError):
            self.service.rename_topic(999, "Missing")

    def test_set_topic_completion(self) -> None:
        t = self.service.create_topic(self.section.id, "Functions")
        self.assertFalse(t.is_completed)

        completed = self.service.set_topic_completion(t.id, True)
        self.assertTrue(completed.is_completed)

        pending = self.service.set_topic_completion(t.id, False)
        self.assertFalse(pending.is_completed)

        with self.assertRaises(TopicNotFoundError):
            self.service.set_topic_completion(999, True)

    def test_delete_topic_success_and_not_found(self) -> None:
        t = self.service.create_topic(self.section.id, "To Delete")
        self.service.delete_topic(t.id)

        with self.assertRaises(TopicNotFoundError):
            self.service.get_topic(t.id)

        with self.assertRaises(TopicNotFoundError):
            self.service.delete_topic(999)


if __name__ == "__main__":
    unittest.main()
