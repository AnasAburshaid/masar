"""JSON file storage implementation."""

import json
import os
from pathlib import Path
import tempfile
from typing import Any

from masar.infrastructure.exceptions import StorageError

DEFAULT_SCHEMA: dict[str, list[dict[str, Any]]] = {
    "journeys": [],
    "sections": [],
    "topics": [],
    "notes": [],
}


class JsonStorage:
    """Handles raw reading, atomic writing, and validation of JSON persistence files."""

    def __init__(self, file_path: str | Path = "masar_data.json") -> None:
        self.file_path = Path(file_path).resolve()

    def load(self) -> dict[str, list[dict[str, Any]]]:
        """Load data from the JSON file or return a blank structure if file doesn't exist."""
        if not self.file_path.exists():
            return {key: [] for key in DEFAULT_SCHEMA}

        try:
            content = self.file_path.read_text(encoding="utf-8")
            data = json.loads(content)
        except (json.JSONDecodeError, OSError) as err:
            raise StorageError(
                f"Corrupted or invalid JSON data in '{self.file_path}': {err}"
            ) from err

        if not isinstance(data, dict):
            raise StorageError(
                f"Corrupted or invalid JSON data in '{self.file_path}': root element must be an object."
            )

        # Ensure all collections are present
        for key in DEFAULT_SCHEMA:
            if key not in data or not isinstance(data[key], list):
                data[key] = []

        return data

    def save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Atomically persist data to the JSON file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file in the same directory, then atomic replace
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                delete=False,
                suffix=".tmp",
            ) as f:
                temp_file = Path(f.name)
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic replace target file
            os.replace(temp_file, self.file_path)
        except Exception as err:
            if temp_file and temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise StorageError(f"Failed to save data to '{self.file_path}': {err}") from err
