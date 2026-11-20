"""Unit and integration tests for PostgreSQL/SQLAlchemy persistence."""

import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from masar.config.settings import Settings
from masar.container import build_container
from masar.domain.exceptions import (
    JourneyNotFoundError,
    NoteNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
)
from masar.domain.models import Journey, Note, Section, Topic
from masar.infrastructure.database.models import JourneyModel, NoteModel, SectionModel, TopicModel
from masar.infrastructure.database.session import Base, get_engine, normalize_database_url
from masar.infrastructure.repositories.database import (
    SqlJourneyRepository,
    SqlNoteRepository,
    SqlSectionRepository,
    SqlTopicRepository,
)
from masar.presentation.api.app import create_app


class TestDatabaseUrlNormalization(unittest.TestCase):
    """Test URL normalization for PostgreSQL drivers."""

    def test_normalize_postgresql_url(self) -> None:
        raw_url = "postgresql://user:pass@localhost:5432/testdb"
        expected = "postgresql+psycopg2://user:pass@localhost:5432/testdb"
        self.assertEqual(normalize_database_url(raw_url), expected)

    def test_normalize_other_urls_unchanged(self) -> None:
        sqlite_url = "sqlite:///:memory:"
        self.assertEqual(normalize_database_url(sqlite_url), sqlite_url)
        pg_custom = "postgresql+asyncpg://user:pass@localhost/db"
        self.assertEqual(normalize_database_url(pg_custom), pg_custom)


class TestSqlRepositories(unittest.TestCase):
    """Test CRUD operations and relationships across all SQL repositories."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session: Session = self.session_factory()

        self.journey_repo = SqlJourneyRepository(self.session)
        self.section_repo = SqlSectionRepository(self.session)
        self.topic_repo = SqlTopicRepository(self.session)
        self.note_repo = SqlNoteRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_journey_repository_crud(self) -> None:
        # Add
        journey = Journey(title="Python Mastery", description="From basics to advanced")
        saved = self.journey_repo.add(journey)
        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.title, "Python Mastery")
        self.assertEqual(saved.description, "From basics to advanced")

        # Get by ID
        fetched = self.journey_repo.get_by_id(saved.id)  # type: ignore[arg-type]
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.title, "Python Mastery")

        # Get non-existent
        self.assertIsNone(self.journey_repo.get_by_id(9999))

        # Get all
        second = self.journey_repo.add(Journey(title="FastAPI Web"))
        all_journeys = self.journey_repo.get_all()
        self.assertEqual(len(all_journeys), 2)
        self.assertEqual([j.title for j in all_journeys], ["Python Mastery", "FastAPI Web"])

        # Update
        saved.title = "Python Mastery Pro"
        saved.description = "Updated description"
        updated = self.journey_repo.update(saved)
        self.assertEqual(updated.title, "Python Mastery Pro")
        self.assertEqual(updated.description, "Updated description")

        # Update non-existent
        with self.assertRaises(JourneyNotFoundError):
            self.journey_repo.update(Journey(id=9999, title="Non-existent"))

        # Update without ID
        with self.assertRaises(ValueError):
            self.journey_repo.update(Journey(title="No ID"))

        # Delete
        self.assertTrue(self.journey_repo.delete(saved.id))  # type: ignore[arg-type]
        self.assertFalse(self.journey_repo.delete(saved.id))  # type: ignore[arg-type]
        self.assertIsNone(self.journey_repo.get_by_id(saved.id))  # type: ignore[arg-type]

    def test_section_repository_crud(self) -> None:
        journey = self.journey_repo.add(Journey(title="Backend Track"))
        assert journey.id is not None

        # Add section
        sec1 = self.section_repo.add(Section(journey_id=journey.id, title="Section 1"))
        sec2 = self.section_repo.add(Section(journey_id=journey.id, title="Section 2"))
        self.assertIsNotNone(sec1.id)
        self.assertEqual(sec1.journey_id, journey.id)

        # Get by ID
        fetched = self.section_repo.get_by_id(sec1.id)  # type: ignore[arg-type]
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.title, "Section 1")
        self.assertIsNone(self.section_repo.get_by_id(8888))

        # Get by journey ID
        sections = self.section_repo.get_by_journey_id(journey.id)
        self.assertEqual(len(sections), 2)
        self.assertEqual([s.title for s in sections], ["Section 1", "Section 2"])

        # Update
        sec1.title = "Foundations"
        updated = self.section_repo.update(sec1)
        self.assertEqual(updated.title, "Foundations")

        # Update non-existent
        with self.assertRaises(SectionNotFoundError):
            self.section_repo.update(Section(id=9999, journey_id=journey.id, title="Missing"))

        # Update without ID
        with self.assertRaises(ValueError):
            self.section_repo.update(Section(journey_id=journey.id, title="Missing ID"))

        # Delete
        self.assertTrue(self.section_repo.delete(sec2.id))  # type: ignore[arg-type]
        self.assertFalse(self.section_repo.delete(sec2.id))  # type: ignore[arg-type]

        # Delete by journey ID
        deleted_count = self.section_repo.delete_by_journey_id(journey.id)
        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(self.section_repo.get_by_journey_id(journey.id)), 0)

    def test_topic_repository_crud(self) -> None:
        journey = self.journey_repo.add(Journey(title="DevOps Track"))
        assert journey.id is not None
        section = self.section_repo.add(Section(journey_id=journey.id, title="Docker"))
        assert section.id is not None

        # Add topic
        topic1 = self.topic_repo.add(Topic(section_id=section.id, title="Containers 101"))
        topic2 = self.topic_repo.add(Topic(section_id=section.id, title="Dockerfile & Compose"))
        self.assertIsNotNone(topic1.id)
        self.assertFalse(topic1.is_completed)

        # Get by ID
        fetched = self.topic_repo.get_by_id(topic1.id)  # type: ignore[arg-type]
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.title, "Containers 101")
        self.assertIsNone(self.topic_repo.get_by_id(9999))

        # Get by section ID
        topics = self.topic_repo.get_by_section_id(section.id)
        self.assertEqual(len(topics), 2)

        # Update
        topic1.title = "Containers Deep Dive"
        topic1.is_completed = True
        updated = self.topic_repo.update(topic1)
        self.assertEqual(updated.title, "Containers Deep Dive")
        self.assertTrue(updated.is_completed)

        # Update non-existent
        with self.assertRaises(TopicNotFoundError):
            self.topic_repo.update(Topic(id=9999, section_id=section.id, title="Ghost"))

        # Update without ID
        with self.assertRaises(ValueError):
            self.topic_repo.update(Topic(section_id=section.id, title="No ID"))

        # Delete
        self.assertTrue(self.topic_repo.delete(topic2.id))  # type: ignore[arg-type]
        self.assertFalse(self.topic_repo.delete(topic2.id))  # type: ignore[arg-type]

        # Delete by section ID
        count = self.topic_repo.delete_by_section_id(section.id)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.topic_repo.get_by_section_id(section.id)), 0)

    def test_note_repository_crud(self) -> None:
        journey = self.journey_repo.add(Journey(title="Frontend Track"))
        assert journey.id is not None
        section = self.section_repo.add(Section(journey_id=journey.id, title="React"))
        assert section.id is not None
        topic = self.topic_repo.add(Topic(section_id=section.id, title="Hooks"))
        assert topic.id is not None

        # Add note
        note1 = self.note_repo.add(Note(topic_id=topic.id, content="Remember useEffect cleanup"))
        note2 = self.note_repo.add(Note(topic_id=topic.id, content="useMemo for heavy calcs"))
        self.assertIsNotNone(note1.id)

        # Get by ID
        fetched = self.note_repo.get_by_id(note1.id)  # type: ignore[arg-type]
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.content, "Remember useEffect cleanup")
        self.assertIsNone(self.note_repo.get_by_id(9999))

        # Get by topic ID
        notes = self.note_repo.get_by_topic_id(topic.id)
        self.assertEqual(len(notes), 2)

        # Update
        note1.update("Updated: Remember useEffect dependencies and cleanup")
        updated = self.note_repo.update(note1)
        self.assertIn("Updated:", updated.content)
        self.assertIsNotNone(updated.updated_at)

        # Update non-existent
        with self.assertRaises(NoteNotFoundError):
            self.note_repo.update(Note(id=9999, topic_id=topic.id, content="Non-existent"))

        # Update without ID
        with self.assertRaises(ValueError):
            self.note_repo.update(Note(topic_id=topic.id, content="No ID"))

        # Delete
        self.assertTrue(self.note_repo.delete(note2.id))  # type: ignore[arg-type]
        self.assertFalse(self.note_repo.delete(note2.id))  # type: ignore[arg-type]

        # Delete by topic ID
        count = self.note_repo.delete_by_topic_id(topic.id)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.note_repo.get_by_topic_id(topic.id)), 0)


class TestContainerAndApiWithDatabase(unittest.TestCase):
    """Test build_container and FastAPI integration with database persistence."""

    def setUp(self) -> None:
        self.db_url = "sqlite://"
        self.settings = Settings(
            storage_type="database",
            database_url=self.db_url,
            environment="testing",
        )

    def test_build_container_database(self) -> None:
        j_srv, s_srv, t_srv, n_srv, p_srv = build_container(
            storage_type="database",
            database_url=self.db_url,
            settings=self.settings,
        )
        created = j_srv.create_journey("Container Journey", "Testing container")
        self.assertIsNotNone(created.id)
        retrieved = j_srv.get_journey(created.id)  # type: ignore[arg-type]
        self.assertEqual(retrieved.title, "Container Journey")

    def test_fastapi_endpoints_with_database_storage(self) -> None:
        app = create_app(self.settings)
        client = TestClient(app)

        # Create journey
        j_resp = client.post("/journeys", json={"title": "DB Journey", "description": "Via API"})
        self.assertEqual(j_resp.status_code, 201)
        j_data = j_resp.json()
        j_id = j_data["id"]
        self.assertEqual(j_data["title"], "DB Journey")

        # Create section
        s_resp = client.post("/sections", json={"journey_id": j_id, "title": "DB Section"})
        self.assertEqual(s_resp.status_code, 201)
        s_id = s_resp.json()["id"]

        # Create topic
        t_resp = client.post("/topics", json={"section_id": s_id, "title": "DB Topic"})
        self.assertEqual(t_resp.status_code, 201)
        t_id = t_resp.json()["id"]

        # Create note
        n_resp = client.post("/notes", json={"topic_id": t_id, "content": "Persisted in SQLite/Postgres DB"})
        self.assertEqual(n_resp.status_code, 201)

        # Check progress
        p_resp = client.get(f"/journeys/{j_id}/progress")
        self.assertEqual(p_resp.status_code, 200)
        self.assertEqual(p_resp.json()["total_topics"], 1)
        self.assertEqual(p_resp.json()["completed_topics"], 0)

        # Mark topic completed
        patch_resp = client.patch(f"/topics/{t_id}/complete")
        self.assertEqual(patch_resp.status_code, 200)
        self.assertTrue(patch_resp.json()["is_completed"])
        p_resp2 = client.get(f"/journeys/{j_id}/progress")
        self.assertEqual(p_resp2.json()["completed_topics"], 1)
        self.assertEqual(p_resp2.json()["percentage"], 100.0)

        # Delete journey (cascading test)
        del_resp = client.delete(f"/journeys/{j_id}")
        self.assertEqual(del_resp.status_code, 204)

        # Verify journey is gone
        self.assertEqual(client.get(f"/journeys/{j_id}").status_code, 404)
