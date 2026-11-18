"""JSON file storage implementation."""

import json
import os
from pathlib import Path
import tempfile
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from masar.application.schemas.storage import validate_storage_data
from masar.domain.exceptions import (
    CorruptedStorageError,
    StorageAccessError,
    StorageError,
)

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
        except OSError as err:
            raise StorageAccessError(
                f"Cannot read storage file at '{self.file_path}': {err}"
            ) from err

        try:
            data = json.loads(content)
        except json.JSONDecodeError as err:
            raise CorruptedStorageError(
                f"Corrupted or invalid JSON data in '{self.file_path}': {err}"
            ) from err

        if not isinstance(data, dict):
            raise CorruptedStorageError(
                f"Corrupted or invalid JSON data in '{self.file_path}': root element must be an object."
            )

        # Ensure all collections are present
        for key in DEFAULT_SCHEMA:
            if key not in data or not isinstance(data[key], list):
                data[key] = []

        try:
            validate_storage_data(data)
        except PydanticValidationError as err:
            raise CorruptedStorageError(
                f"Corrupted or invalid schema in storage file '{self.file_path}': {err}"
            ) from err

        return data

    def save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Atomically persist data to the JSON file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise StorageAccessError(
                f"Cannot create directory '{self.file_path.parent}': {err}"
            ) from err

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
        except OSError as err:
            if temp_file and temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise StorageAccessError(f"Failed to save data to '{self.file_path}': {err}") from err
        except Exception as err:
            if temp_file and temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise StorageError(f"Failed to save data to '{self.file_path}': {err}") from err
