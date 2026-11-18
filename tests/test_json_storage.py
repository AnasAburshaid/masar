"""Tests for JSON persistence storage engine."""

import json
from pathlib import Path
import tempfile
import unittest

from masar.infrastructure.exceptions import StorageError
from masar.infrastructure.storage.json_storage import JsonStorage


class TestJsonStorage(unittest.TestCase):
    """Test suite for JsonStorage engine."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "test_data.json"
        self.storage = JsonStorage(self.file_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_nonexistent_file_returns_empty_structure(self) -> None:
        data = self.storage.load()
        self.assertEqual(data, {"journeys": [], "sections": [], "topics": [], "notes": []})
        self.assertFalse(self.file_path.exists())

    def test_save_and_load_roundtrip(self) -> None:
        sample_data = {
            "journeys": [{"id": 1, "title": "Python", "description": "Basics", "created_at": "2026-11-18T20:00:00+00:00"}],
            "sections": [{"id": 1, "journey_id": 1, "title": "Intro"}],
            "topics": [{"id": 1, "section_id": 1, "title": "Variables", "is_completed": False}],
            "notes": [{"id": 1, "topic_id": 1, "content": "Note text", "created_at": "2026-11-18T20:00:00+00:00", "updated_at": None}],
        }
        self.storage.save(sample_data)
        self.assertTrue(self.file_path.exists())

        loaded = self.storage.load()
        self.assertEqual(loaded, sample_data)

    def test_load_corrupted_json_raises_storage_error(self) -> None:
        self.file_path.write_text("{invalid_json: true", encoding="utf-8")
        with self.assertRaises(StorageError) as ctx:
            self.storage.load()
        self.assertIn("Corrupted or invalid JSON", str(ctx.exception))

    def test_load_invalid_root_type_raises_storage_error(self) -> None:
        self.file_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
        with self.assertRaises(StorageError):
            self.storage.load()

    def test_save_creates_parent_directory_if_needed(self) -> None:
        nested_path = Path(self.temp_dir.name) / "sub" / "dir" / "nested.json"
        storage = JsonStorage(nested_path)
        storage.save({"journeys": [], "sections": [], "topics": [], "notes": []})
        self.assertTrue(nested_path.exists())


if __name__ == "__main__":
    unittest.main()
