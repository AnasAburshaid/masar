"""Pydantic validation schemas for User registration and responses."""

import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserRegisterSchema(BaseModel):
    """Schema for user registration requests."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(
        ...,
        max_length=255,
        description="User email address",
        examples=["developer@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        trimmed = value.strip().lower()
        if not trimmed:
            raise ValueError("Email cannot be empty.")
        if not EMAIL_REGEX.match(trimmed):
            raise ValueError("Invalid email address format.")
        return trimmed

    @field_validator("password")
    @classmethod
    def validate_password_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password cannot consist of whitespace only.")
        return value


class UserResponseSchema(BaseModel):
    """Schema for user response representation without sensitive credentials."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int = Field(..., gt=0, description="User unique identifier")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(default=True, description="Whether user account is active")
    created_at: datetime = Field(..., description="Timestamp when account was created")
