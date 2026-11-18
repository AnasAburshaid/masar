"""Tests for domain models and business validation rules."""

import unittest

from masar.domain.exceptions import ValidationError
from masar.domain.models import Journey, Section, Topic


class TestJourneyDomain(unittest.TestCase):
    """Test cases for the Journey domain entity."""

    def test_create_valid_journey(self) -> None:
        journey = Journey(title="Python Mastery", description="Learn Python deeply")
        self.assertEqual(journey.title, "Python Mastery")
        self.assertEqual(journey.description, "Learn Python deeply")
        self.assertIsNone(journey.id)
        self.assertIsNotNone(journey.created_at)

    def test_create_journey_whitespace_trimmed(self) -> None:
        journey = Journey(title="  Backend Development  ", description="  REST APIs  ")
        self.assertEqual(journey.title, "Backend Development")
        self.assertEqual(journey.description, "REST APIs")

    def test_create_journey_empty_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            Journey(title="")
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_create_journey_whitespace_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            Journey(title="   ")
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_update_journey_valid(self) -> None:
        journey = Journey(title="Python", description="Basics")
        journey.update(title="Advanced Python", description="Concurrency and metaprogramming")
        self.assertEqual(journey.title, "Advanced Python")
        self.assertEqual(journey.description, "Concurrency and metaprogramming")

    def test_update_journey_empty_title_raises_validation_error(self) -> None:
        journey = Journey(title="Python", description="Basics")
        with self.assertRaises(ValidationError):
            journey.update(title="   ")


class TestSectionDomain(unittest.TestCase):
    """Test cases for the Section domain entity."""

    def test_create_valid_section(self) -> None:
        section = Section(journey_id=1, title="Python Fundamentals")
        self.assertEqual(section.journey_id, 1)
        self.assertEqual(section.title, "Python Fundamentals")
        self.assertIsNone(section.id)
        self.assertIsNotNone(section.created_at)

    def test_create_section_whitespace_trimmed(self) -> None:
        section = Section(journey_id=1, title="   Fundamentals   ")
        self.assertEqual(section.title, "Fundamentals")

    def test_create_section_empty_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Section(journey_id=1, title="")
        with self.assertRaises(ValidationError):
            Section(journey_id=1, title="    ")

    def test_rename_section_valid_and_invalid(self) -> None:
        section = Section(journey_id=1, title="Initial Title")
        section.rename("Advanced OOP")
        self.assertEqual(section.title, "Advanced OOP")

        with self.assertRaises(ValidationError):
            section.rename("  ")


class TestTopicDomain(unittest.TestCase):
    """Test cases for the Topic domain entity."""

    def test_create_valid_topic(self) -> None:
        topic = Topic(section_id=1, title="Variables")
        self.assertEqual(topic.section_id, 1)
        self.assertEqual(topic.title, "Variables")
        self.assertFalse(topic.is_completed)
        self.assertIsNone(topic.id)
        self.assertIsNotNone(topic.created_at)

    def test_create_topic_whitespace_trimmed(self) -> None:
        topic = Topic(section_id=1, title="   Data Types   ")
        self.assertEqual(topic.title, "Data Types")

    def test_create_topic_empty_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Topic(section_id=1, title="")
        with self.assertRaises(ValidationError):
            Topic(section_id=1, title="   ")

    def test_rename_topic(self) -> None:
        topic = Topic(section_id=1, title="Variables")
        topic.rename("Variables & Constants")
        self.assertEqual(topic.title, "Variables & Constants")

        with self.assertRaises(ValidationError):
            topic.rename("   ")

    def test_topic_completion_status_mutations(self) -> None:
        topic = Topic(section_id=1, title="Functions")
        self.assertFalse(topic.is_completed)

        topic.mark_completed()
        self.assertTrue(topic.is_completed)

        topic.mark_pending()
        self.assertFalse(topic.is_completed)

        topic.set_status(True)
        self.assertTrue(topic.is_completed)

        topic.set_status(False)
        self.assertFalse(topic.is_completed)


if __name__ == "__main__":
    unittest.main()
