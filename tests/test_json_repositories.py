"""Tests for JSON repository implementations."""

from pathlib import Path
import tempfile
import unittest

from masar.domain.exceptions import (
    JourneyNotFoundError,
    NoteNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Journey, Note, Section, Topic
from masar.infrastructure.repositories.json import (
    JsonJourneyRepository,
    JsonNoteRepository,
    JsonSectionRepository,
    JsonTopicRepository,
)
from masar.infrastructure.storage.json_storage import JsonStorage


class TestJsonRepositories(unittest.TestCase):
    """Test suite for concrete JSON repository implementations and persistence."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "masar_test.json"
        self.storage = JsonStorage(self.file_path)
        self.journey_repo = JsonJourneyRepository(self.storage)
        self.section_repo = JsonSectionRepository(self.storage)
        self.topic_repo = JsonTopicRepository(self.storage)
        self.note_repo = JsonNoteRepository(self.storage)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_journey_repository_crud_and_persistence(self) -> None:
        j1 = Journey(title="Python Track", description="Learn Python")
        added = self.journey_repo.add(j1)
        self.assertEqual(added.id, 1)

        # Get by id
        found = self.journey_repo.get_by_id(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Python Track")

        # Get all
        all_j = self.journey_repo.get_all()
        self.assertEqual(len(all_j), 1)

        # Update
        found.update(title="Advanced Python")
        updated = self.journey_repo.update(found)
        self.assertEqual(updated.title, "Advanced Python")

        # Persistence across restart (fresh repository instance)
        new_storage = JsonStorage(self.file_path)
        restarted_repo = JsonJourneyRepository(new_storage)
        survived = restarted_repo.get_by_id(1)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.title, "Advanced Python")

        # Add second journey auto-increments
        j2 = Journey(title="FastAPI Track")
        added2 = restarted_repo.add(j2)
        self.assertEqual(added2.id, 2)

        # Delete
        self.assertTrue(restarted_repo.delete(1))
        self.assertIsNone(restarted_repo.get_by_id(1))
        self.assertFalse(restarted_repo.delete(999))

        # Update nonexistent raises
        with self.assertRaises(JourneyNotFoundError):
            restarted_repo.update(found)

    def test_section_repository_crud_and_persistence(self) -> None:
        s1 = Section(journey_id=1, title="Basics")
        s2 = Section(journey_id=1, title="Advanced")
        s3 = Section(journey_id=2, title="Other")

        self.section_repo.add(s1)
        self.section_repo.add(s2)
        self.section_repo.add(s3)

        self.assertEqual(len(self.section_repo.get_by_journey_id(1)), 2)
        self.assertEqual(len(self.section_repo.get_by_journey_id(2)), 1)

        # Update
        s1.rename("Python Basics")
        self.section_repo.update(s1)

        # Restart check
        restarted_repo = JsonSectionRepository(JsonStorage(self.file_path))
        self.assertEqual(restarted_repo.get_by_id(1).title, "Python Basics")

        # Delete by journey id
        deleted_count = restarted_repo.delete_by_journey_id(1)
        self.assertEqual(deleted_count, 2)
        self.assertEqual(len(restarted_repo.get_by_journey_id(1)), 0)
        self.assertEqual(len(restarted_repo.get_by_journey_id(2)), 1)

        # Update nonexistent raises
        with self.assertRaises(SectionNotFoundError):
            restarted_repo.update(s1)

    def test_topic_repository_crud_and_persistence(self) -> None:
        t1 = Topic(section_id=1, title="Variables")
        t2 = Topic(section_id=1, title="Functions")
        self.topic_repo.add(t1)
        self.topic_repo.add(t2)

        self.assertEqual(len(self.topic_repo.get_by_section_id(1)), 2)

        # Completion status update
        t1.mark_completed()
        self.topic_repo.update(t1)

        # Restart check
        restarted_repo = JsonTopicRepository(JsonStorage(self.file_path))
        restarted_t1 = restarted_repo.get_by_id(1)
        self.assertTrue(restarted_t1.is_completed)

        # Delete by section id
        deleted_count = restarted_repo.delete_by_section_id(1)
        self.assertEqual(deleted_count, 2)
        self.assertEqual(len(restarted_repo.get_by_section_id(1)), 0)

        # Update nonexistent raises
        with self.assertRaises(TopicNotFoundError):
            restarted_repo.update(t1)

    def test_note_repository_crud_and_persistence(self) -> None:
        n1 = Note(topic_id=1, content="Important note")
        n2 = Note(topic_id=1, content="Second note")
        self.note_repo.add(n1)
        self.note_repo.add(n2)

        self.assertEqual(len(self.note_repo.get_by_topic_id(1)), 2)

        n1.update("Updated content")
        self.note_repo.update(n1)

        # Restart check
        restarted_repo = JsonNoteRepository(JsonStorage(self.file_path))
        restarted_n1 = restarted_repo.get_by_id(1)
        self.assertEqual(restarted_n1.content, "Updated content")

        # Delete by topic id
        deleted_count = restarted_repo.delete_by_topic_id(1)
        self.assertEqual(deleted_count, 2)
        self.assertEqual(len(restarted_repo.get_by_topic_id(1)), 0)

        # Update nonexistent raises
        with self.assertRaises(NoteNotFoundError):
            restarted_repo.update(n1)


if __name__ == "__main__":
    unittest.main()
