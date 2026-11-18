"""Tests for enhanced validation rules and domain exception hierarchy."""

from pathlib import Path
import tempfile
import unittest

from masar.domain.exceptions import (
    CorruptedStorageError,
    DomainError,
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    StorageAccessError,
    StorageError,
    ValidationError,
)
from masar.domain.models import Journey, Note, Section, Topic
from masar.infrastructure.storage.json_storage import JsonStorage


class TestValidationAndExceptions(unittest.TestCase):
    """Test suite for granular validation rules and custom exceptions."""

    def test_exception_inheritance_hierarchy(self) -> None:
        """Verify new granular exceptions properly inherit from base exceptions."""
        self.assertTrue(issubclass(EmptyFieldError, ValidationError))
        self.assertTrue(issubclass(FieldLengthError, ValidationError))
        self.assertTrue(issubclass(InvalidIdError, ValidationError))
        self.assertTrue(issubclass(ValidationError, DomainError))

        self.assertTrue(issubclass(CorruptedStorageError, StorageError))
        self.assertTrue(issubclass(StorageAccessError, StorageError))
        self.assertTrue(issubclass(StorageError, DomainError))

    def test_journey_empty_title_raises_empty_field_error(self) -> None:
        with self.assertRaises(EmptyFieldError):
            Journey(title="")
        with self.assertRaises(EmptyFieldError):
            Journey(title="   ")

    def test_journey_excessive_title_length_raises_field_length_error(self) -> None:
        long_title = "A" * 101
        with self.assertRaises(FieldLengthError):
            Journey(title=long_title)

    def test_journey_excessive_description_raises_field_length_error(self) -> None:
        long_desc = "D" * 1001
        with self.assertRaises(FieldLengthError):
            Journey(title="Python", description=long_desc)

    def test_journey_invalid_id_raises_invalid_id_error(self) -> None:
        with self.assertRaises(InvalidIdError):
            Journey(title="Python", id=0)
        with self.assertRaises(InvalidIdError):
            Journey(title="Python", id=-1)

    def test_section_validation_rules(self) -> None:
        # Invalid journey_id
        with self.assertRaises(InvalidIdError):
            Section(journey_id=0, title="Basics")
        with self.assertRaises(InvalidIdError):
            Section(journey_id=-5, title="Basics")

        # Empty title
        with self.assertRaises(EmptyFieldError):
            Section(journey_id=1, title="")

        # Long title
        with self.assertRaises(FieldLengthError):
            Section(journey_id=1, title="S" * 101)

        # Invalid section ID
        with self.assertRaises(InvalidIdError):
            Section(journey_id=1, title="Basics", id=-1)

    def test_topic_validation_rules(self) -> None:
        # Invalid section_id
        with self.assertRaises(InvalidIdError):
            Topic(section_id=0, title="Variables")
        with self.assertRaises(InvalidIdError):
            Topic(section_id=-1, title="Variables")

        # Empty title
        with self.assertRaises(EmptyFieldError):
            Topic(section_id=1, title="")

        # Long title
        with self.assertRaises(FieldLengthError):
            Topic(section_id=1, title="T" * 101)

        # Invalid topic ID
        with self.assertRaises(InvalidIdError):
            Topic(section_id=1, title="Variables", id=0)

    def test_note_validation_rules(self) -> None:
        # Invalid topic_id
        with self.assertRaises(InvalidIdError):
            Note(topic_id=0, content="Some content")
        with self.assertRaises(InvalidIdError):
            Note(topic_id=-2, content="Some content")

        # Empty content
        with self.assertRaises(EmptyFieldError):
            Note(topic_id=1, content="")

        # Long content
        with self.assertRaises(FieldLengthError):
            Note(topic_id=1, content="N" * 5001)

        # Invalid note ID
        with self.assertRaises(InvalidIdError):
            Note(topic_id=1, content="Content", id=-10)

    def test_json_storage_raises_corrupted_storage_error_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_file = Path(temp_dir) / "corrupt.json"
            bad_file.write_text("{not: valid json", encoding="utf-8")
            storage = JsonStorage(bad_file)
            with self.assertRaises(CorruptedStorageError):
                storage.load()

    def test_json_storage_raises_corrupted_storage_error_on_non_dict_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            array_file = Path(temp_dir) / "array.json"
            array_file.write_text("[1, 2, 3]", encoding="utf-8")
            storage = JsonStorage(array_file)
            with self.assertRaises(CorruptedStorageError):
                storage.load()


if __name__ == "__main__":
    unittest.main()
