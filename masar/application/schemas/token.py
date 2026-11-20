"""Pydantic schemas for authentication tokens and login requests."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequestSchema(BaseModel):
    """Schema for user login credentials."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., max_length=255, description="Registered user email address")
    password: str = Field(..., min_length=1, description="User account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        trimmed = value.strip().lower()
        if not trimmed:
            raise ValueError("Email cannot be empty.")
        return trimmed


class TokenResponseSchema(BaseModel):
    """Schema representing an issued JWT access token."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(..., description="Encoded JWT access token")
    token_type: str = Field(default="bearer", description="Token type prefix (typically 'bearer')")
