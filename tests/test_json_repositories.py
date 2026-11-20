"""Tests for JSON repository implementations."""

from pathlib import Path
import tempfile
import unittest

from masar.domain.exceptions import (
    JourneyNotFoundError,
    NoteNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
    UserAlreadyExistsError,
)
from masar.domain.models import Document, Journey, Note, ProfileItem, Section, Topic, User
from masar.infrastructure.repositories.json import (
    JsonDocumentRepository,
    JsonJourneyRepository,
    JsonNoteRepository,
    JsonProfileRepository,
    JsonSectionRepository,
    JsonTopicRepository,
    JsonUserRepository,
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
        self.user_repo = JsonUserRepository(self.storage)
        self.doc_repo = JsonDocumentRepository(self.storage)
        self.profile_repo = JsonProfileRepository(self.storage)

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

    def test_user_repository_crud_and_persistence(self) -> None:
        user1 = User(email="Alice@Example.com", hashed_password="pbkdf2:sha256:hash1")
        added = self.user_repo.add(user1)
        self.assertEqual(added.id, 1)

        # Case-insensitive lookup
        found = self.user_repo.get_by_email("alice@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found.email, "alice@example.com")
        self.assertEqual(found.hashed_password, "pbkdf2:sha256:hash1")

        # Duplicate email raises
        dup = User(email="alice@example.com", hashed_password="pbkdf2:sha256:hash2")
        with self.assertRaises(UserAlreadyExistsError):
            self.user_repo.add(dup)

        # Persistence across restart
        new_storage = JsonStorage(self.file_path)
        restarted_repo = JsonUserRepository(new_storage)
        survived = restarted_repo.get_by_id(1)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.hashed_password, "pbkdf2:sha256:hash1")

        # Second user auto-increments
        user2 = User(email="bob@example.com", hashed_password="pbkdf2:sha256:hash2")
        added2 = restarted_repo.add(user2)
        self.assertEqual(added2.id, 2)

        # Get all
        all_users = restarted_repo.get_all()
        self.assertEqual(len(all_users), 2)

        # Delete
        self.assertTrue(restarted_repo.delete(1))
        self.assertIsNone(restarted_repo.get_by_id(1))
        self.assertFalse(restarted_repo.delete(999))

    def test_document_repository_crud_and_persistence(self) -> None:
        doc = Document(
            user_id=1,
            filename="syllabus.md",
            file_type="markdown",
            file_size_bytes=1024,
            extracted_text="# Syllabus\nContent",
        )
        added = self.doc_repo.add(doc)
        self.assertEqual(added.id, 1)

        # Get by id
        found = self.doc_repo.get_by_id(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.filename, "syllabus.md")

        # List by user id
        user1_docs = self.doc_repo.list_by_user_id(1)
        self.assertEqual(len(user1_docs), 1)
        user2_docs = self.doc_repo.list_by_user_id(2)
        self.assertEqual(len(user2_docs), 0)

        # Update
        found.update_summary("AI Summary")
        updated = self.doc_repo.update(found)
        self.assertEqual(updated.summary, "AI Summary")

        # Persistence across restart
        new_storage = JsonStorage(self.file_path)
        restarted_repo = JsonDocumentRepository(new_storage)
        survived = restarted_repo.get_by_id(1)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.summary, "AI Summary")

        # Delete
        self.assertTrue(restarted_repo.delete(1))
        self.assertIsNone(restarted_repo.get_by_id(1))

    def test_profile_repository_crud_and_persistence(self) -> None:
        user = self.user_repo.add(User(email="alice@example.com", hashed_password="hash"))
        user_id = user.id or 1

        item = ProfileItem(
            user_id=user_id,
            name="TypeScript",
            category="language",
            level="intermediate",
            is_confirmed=True,
            source_type="manual",
        )
        added = self.profile_repo.add_item(item)
        self.assertEqual(added.id, 1)

        # Get item
        fetched = self.profile_repo.get_item(1)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.name, "TypeScript")

        # Update item
        fetched.level = "advanced"
        updated = self.profile_repo.update_item(fetched)
        self.assertEqual(updated.level, "advanced")

        # Update bio
        self.profile_repo.update_bio(user_id, "Full-Stack Dev")
        profile = self.profile_repo.get_profile(user_id)
        self.assertEqual(profile.bio, "Full-Stack Dev")
        self.assertEqual(len(profile.items), 1)

        # Persistence across restart
        new_storage = JsonStorage(self.file_path)
        restarted_repo = JsonProfileRepository(new_storage)
        survived_profile = restarted_repo.get_profile(user_id)
        self.assertEqual(survived_profile.bio, "Full-Stack Dev")
        self.assertEqual(len(survived_profile.items), 1)
        self.assertEqual(survived_profile.items[0].level, "advanced")

        # Delete
        self.assertTrue(restarted_repo.delete_item(1))
        self.assertIsNone(restarted_repo.get_item(1))
        self.assertFalse(restarted_repo.delete_item(9999))



if __name__ == "__main__":
    unittest.main()
