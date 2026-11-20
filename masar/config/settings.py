"""Centralized application settings and configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import AliasChoices, Field
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
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins for frontend-backend communication",
    )
    ai_provider: Literal["openrouter", "mock"] = Field(
        default="openrouter",
        description="Active AI/LLM provider backend ('openrouter' or 'mock')",
    )
    ai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "OPENROUTER_API-KEY",
            "OPENROUTER_API_KEY",
            "MASAR_AI_API_KEY",
            "AI_API_KEY",
        ),
        description="API key for AI provider (e.g. OpenRouter)",
    )
    ai_model: str = Field(
        default="nvidia/nemotron-3-ultra-550b-a55b:free",
        validation_alias=AliasChoices("MASAR_AI_MODEL", "AI_MODEL"),
        description="Default AI model identifier",
    )
    ai_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias=AliasChoices("MASAR_AI_BASE_URL", "AI_BASE_URL"),
        description="Base URL for OpenAI-compatible or OpenRouter API",
    )
    ai_timeout_seconds: float = Field(
        default=30.0,
        validation_alias=AliasChoices("MASAR_AI_TIMEOUT_SECONDS", "AI_TIMEOUT_SECONDS"),
        description="HTTP request timeout in seconds for AI completions",
    )
    ai_temperature: float = Field(
        default=0.7,
        validation_alias=AliasChoices("MASAR_AI_TEMPERATURE", "AI_TEMPERATURE"),
        description="Default sampling temperature for AI completions",
    )
    ai_max_tokens: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("MASAR_AI_MAX_TOKENS", "AI_MAX_TOKENS"),
        description="Maximum tokens to generate",
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
