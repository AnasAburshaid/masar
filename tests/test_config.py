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
        # Clean up any MASAR_ or OPENROUTER_ env vars
        self.old_env = {}
        for key in list(os.environ.keys()):
            if key.startswith("MASAR_") or key.startswith("OPENROUTER_") or key == "AI_API_KEY":
                self.old_env[key] = os.environ.pop(key)

    def tearDown(self) -> None:
        clear_settings_cache()
        for key in list(os.environ.keys()):
            if key.startswith("MASAR_") or key.startswith("OPENROUTER_") or key == "AI_API_KEY":
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

    def test_ai_settings_defaults(self) -> None:
        settings = Settings()
        self.assertEqual(settings.ai_provider, "openrouter")
        self.assertEqual(settings.ai_model, "nvidia/nemotron-3-ultra-550b-a55b:free")
        self.assertEqual(settings.ai_base_url, "https://openrouter.ai/api/v1")
        self.assertEqual(settings.ai_timeout_seconds, 30.0)
        self.assertEqual(settings.ai_temperature, 0.7)

    def test_ai_settings_env_overrides(self) -> None:
        os.environ["MASAR_AI_PROVIDER"] = "mock"
        os.environ["MASAR_AI_MODEL"] = "custom-nemotron"
        os.environ["OPENROUTER_API_KEY"] = "sk-test-alias-key"
        os.environ["MASAR_AI_TIMEOUT_SECONDS"] = "45.0"

        settings = Settings()
        self.assertEqual(settings.ai_provider, "mock")
        self.assertEqual(settings.ai_model, "custom-nemotron")
        self.assertEqual(settings.ai_api_key, "sk-test-alias-key")
        self.assertEqual(settings.ai_timeout_seconds, 45.0)

    def test_ai_invalid_provider_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(ai_provider="invalid_ai")  # type: ignore[arg-type]



if __name__ == "__main__":
    unittest.main()
