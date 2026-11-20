"""Centralized application settings and configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    app_name: str = Field(
        default="Masar - Developer Learning Tracker",
        description="Application title and display name",
    )
    storage_type: Literal["json", "in_memory", "database", "postgres"] = Field(
        default="json",
        description="Persistence storage mechanism ('json', 'in_memory', or 'database')",
    )
    data_file: Path = Field(
        default=Path("masar_data.json"),
        description="Path to persistence JSON file",
    )
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/masar",
        description="PostgreSQL or SQLAlchemy database connection URL",
    )
    jwt_secret_key: str = Field(
        default="masar-insecure-default-dev-secret-change-in-production",
        description="Secret key used for signing JWT access tokens",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Cryptographic algorithm for JWT encoding/decoding",
    )
    jwt_expire_minutes: int = Field(
        default=60,
        description="Access token expiration time in minutes",
    )
    environment: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Current runtime environment",
    )
    strict_auth: bool = Field(
        default=False,
        description="Enforce strict authentication rejecting anonymous requests even in testing environment",
    )

    model_config = SettingsConfigDict(
        env_prefix="MASAR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings instance."""
    return Settings()


def clear_settings_cache() -> None:
    """Clear the cached settings instance (useful in tests)."""
    get_settings.cache_clear()
