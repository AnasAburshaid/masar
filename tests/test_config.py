"""Tests for application configuration and environment settings."""

import os
from pathlib import Path
import unittest

from pydantic import ValidationError

from masar.config.settings import Settings, clear_settings_cache, get_settings
from masar.container import build_cli, build_container


class TestConfigAndSettings(unittest.TestCase):
    """Test suite for centralized Settings management."""

    def setUp(self) -> None:
        clear_settings_cache()
        # Clean up any MASAR_ env vars
        self.old_env = {}
        for key in list(os.environ.keys()):
            if key.startswith("MASAR_"):
                self.old_env[key] = os.environ.pop(key)

    def tearDown(self) -> None:
        clear_settings_cache()
        for key in list(os.environ.keys()):
            if key.startswith("MASAR_"):
                os.environ.pop(key, None)
        for key, val in self.old_env.items():
            os.environ[key] = val

    def test_default_settings(self) -> None:
        settings = Settings()
        self.assertEqual(settings.app_name, "Masar - Developer Learning Tracker")
        self.assertEqual(settings.storage_type, "json")
        self.assertEqual(settings.data_file, Path("masar_data.json"))
        self.assertEqual(settings.environment, "development")

    def test_environment_variable_overrides(self) -> None:
        os.environ["MASAR_APP_NAME"] = "Custom Tracker"
        os.environ["MASAR_STORAGE_TYPE"] = "in_memory"
        os.environ["MASAR_DATA_FILE"] = "test_custom_data.json"
        os.environ["MASAR_ENVIRONMENT"] = "testing"

        settings = Settings()
        self.assertEqual(settings.app_name, "Custom Tracker")
        self.assertEqual(settings.storage_type, "in_memory")
        self.assertEqual(settings.data_file, Path("test_custom_data.json"))
        self.assertEqual(settings.environment, "testing")

    def test_invalid_storage_type_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(storage_type="unsupported_type")  # type: ignore[arg-type]

    def test_get_settings_caching_and_clearing(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        self.assertIs(s1, s2)

        clear_settings_cache()
        s3 = get_settings()
        self.assertIsNot(s1, s3)

    def test_container_respects_custom_settings(self) -> None:
        custom_settings = Settings(storage_type="in_memory")
        services = build_container(settings=custom_settings)
        self.assertEqual(len(services), 5)

        cli = build_cli(settings=custom_settings)
        self.assertIsNotNone(cli)


if __name__ == "__main__":
    unittest.main()
