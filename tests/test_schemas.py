"""Tests for Pydantic input, response, and storage validation schemas."""

from datetime import datetime
import unittest

from pydantic import ValidationError

from masar.application.schemas import (
    JourneyCreateSchema,
    JourneyResponseSchema,
    JourneyUpdateSchema,
    NoteCreateSchema,
    NoteResponseSchema,
    NoteUpdateSchema,
    SectionCreateSchema,
    SectionResponseSchema,
    SectionUpdateSchema,
    StorageDataSchema,
    TopicCreateSchema,
    TopicResponseSchema,
    TopicUpdateSchema,
    validate_storage_data,
)
from masar.domain.models.journey import Journey
from masar.domain.models.note import Note
from masar.domain.models.section import Section
from masar.domain.models.topic import Topic


class TestPydanticSchemas(unittest.TestCase):
    """Test suite for application Pydantic schemas."""

    # ---------------- Journey Schemas ----------------

    def test_journey_create_schema_valid(self) -> None:
        schema = JourneyCreateSchema(title="  Clean Code  ", description="  Book summary  ")
        self.assertEqual(schema.title, "Clean Code")
        self.assertEqual(schema.description, "Book summary")

    def test_journey_create_schema_empty_title_fails(self) -> None:
        with self.assertRaises(ValidationError):
            JourneyCreateSchema(title="")
        with self.assertRaises(ValidationError):
            JourneyCreateSchema(title="   ")

    def test_journey_create_schema_length_bounds(self) -> None:
        with self.assertRaises(ValidationError):
            JourneyCreateSchema(title="a" * 101)
        with self.assertRaises(ValidationError):
            JourneyCreateSchema(title="Valid", description="b" * 1001)

    def test_journey_update_schema_optional_fields(self) -> None:
        schema = JourneyUpdateSchema(title="Updated Title")
        self.assertEqual(schema.title, "Updated Title")
        self.assertIsNone(schema.description)

        empty_update = JourneyUpdateSchema()
        self.assertIsNone(empty_update.title)
        self.assertIsNone(empty_update.description)

    def test_journey_response_schema_from_domain_entity(self) -> None:
        entity = Journey(id=1, title="FastAPI", description="API Guide")
        schema = JourneyResponseSchema.model_validate(entity)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.title, "FastAPI")
        self.assertEqual(schema.description, "API Guide")

    # ---------------- Section Schemas ----------------

    def test_section_create_schema_valid_and_bounds(self) -> None:
        schema = SectionCreateSchema(journey_id=1, title="Routing", order=2)
        self.assertEqual(schema.journey_id, 1)
        self.assertEqual(schema.title, "Routing")
        self.assertEqual(schema.order, 2)

        # Non-positive journey_id
        with self.assertRaises(ValidationError):
            SectionCreateSchema(journey_id=0, title="Routing")
        with self.assertRaises(ValidationError):
            SectionCreateSchema(journey_id=-1, title="Routing")

        # Exceeds max length
        with self.assertRaises(ValidationError):
            SectionCreateSchema(journey_id=1, title="a" * 101)

        # Negative order
        with self.assertRaises(ValidationError):
            SectionCreateSchema(journey_id=1, title="Routing", order=-1)

    def test_section_response_schema_from_domain_entity(self) -> None:
        entity = Section(id=1, journey_id=10, title="Architecture")
        schema = SectionResponseSchema.model_validate(entity)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.journey_id, 10)
        self.assertEqual(schema.title, "Architecture")

    # ---------------- Topic Schemas ----------------

    def test_topic_create_schema_valid_and_bounds(self) -> None:
        schema = TopicCreateSchema(section_id=2, title="Dependency Injection", order=1, is_completed=True)
        self.assertEqual(schema.section_id, 2)
        self.assertEqual(schema.title, "Dependency Injection")
        self.assertTrue(schema.is_completed)

        with self.assertRaises(ValidationError):
            TopicCreateSchema(section_id=0, title="Dependency Injection")

        with self.assertRaises(ValidationError):
            TopicCreateSchema(section_id=1, title="x" * 101)

    def test_topic_response_schema_from_domain_entity(self) -> None:
        entity = Topic(id=5, section_id=2, title="Lifespan Events", is_completed=True)
        schema = TopicResponseSchema.model_validate(entity)
        self.assertEqual(schema.id, 5)
        self.assertEqual(schema.section_id, 2)
        self.assertEqual(schema.title, "Lifespan Events")
        self.assertTrue(schema.is_completed)

    # ---------------- Note Schemas ----------------

    def test_note_create_schema_valid_and_bounds(self) -> None:
        schema = NoteCreateSchema(topic_id=3, content="Remember to use async context manager.")
        self.assertEqual(schema.topic_id, 3)
        self.assertEqual(schema.content, "Remember to use async context manager.")

        # Non-positive topic_id
        with self.assertRaises(ValidationError):
            NoteCreateSchema(topic_id=0, content="Content")

        # Empty content
        with self.assertRaises(ValidationError):
            NoteCreateSchema(topic_id=1, content="   ")

        # Exceeds max length
        with self.assertRaises(ValidationError):
            NoteCreateSchema(topic_id=1, content="x" * 5001)

    def test_note_update_schema(self) -> None:
        schema = NoteUpdateSchema(content="Revised notes")
        self.assertEqual(schema.content, "Revised notes")

        with self.assertRaises(ValidationError):
            NoteUpdateSchema(content="")

    def test_note_response_schema_from_domain_entity(self) -> None:
        entity = Note(id=7, topic_id=3, content="Key takeaway")
        schema = NoteResponseSchema.model_validate(entity)
        self.assertEqual(schema.id, 7)
        self.assertEqual(schema.topic_id, 3)
        self.assertEqual(schema.content, "Key takeaway")

    # ---------------- Storage Schemas ----------------

    def test_storage_data_schema_valid_structure(self) -> None:
        raw_data = {
            "journeys": [{"id": 1, "title": "Python Basics", "description": "Intro"}],
            "sections": [{"id": 1, "journey_id": 1, "title": "Syntax", "order": 0}],
            "topics": [{"id": 1, "section_id": 1, "title": "Variables", "order": 0, "completed": False}],
            "notes": [{"id": 1, "topic_id": 1, "content": "Sample note"}],
        }
        validated = validate_storage_data(raw_data)
        self.assertIsInstance(validated, StorageDataSchema)
        self.assertEqual(len(validated.journeys), 1)
        self.assertEqual(validated.journeys[0].id, 1)
        self.assertEqual(validated.journeys[0].title, "Python Basics")

    def test_storage_data_schema_invalid_record_raises_validation_error(self) -> None:
        raw_data = {
            "journeys": [{"id": -99, "title": "Invalid ID"}],
            "sections": [],
            "topics": [],
            "notes": [],
        }
        with self.assertRaises(ValidationError):
            validate_storage_data(raw_data)


if __name__ == "__main__":
    unittest.main()
