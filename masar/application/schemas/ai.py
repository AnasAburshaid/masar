"""Pydantic validation schemas for AI completion and chat."""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatMessageSchema(BaseModel):
    """Schema representing an individual chat message."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Role of the message author ('system', 'user', or 'assistant')",
    )
    content: str = Field(..., min_length=1, description="Text content of the message")


class CompletionRequestSchema(BaseModel):
    """Schema for a single prompt completion request."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(..., min_length=1, description="Prompt text to be completed by the LLM")
    system_prompt: Optional[str] = Field(default=None, description="Optional system instruction")
    model: Optional[str] = Field(default=None, description="Optional override for model identifier")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, gt=0, description="Maximum tokens to generate")


class ChatRequestSchema(BaseModel):
    """Schema for a multi-turn chat request."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    messages: list[ChatMessageSchema] = Field(..., min_length=1, description="List of conversational messages")
    model: Optional[str] = Field(default=None, description="Optional override for model identifier")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, gt=0, description="Maximum tokens to generate")


class AIUsageSchema(BaseModel):
    """Schema representing token consumption statistics."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class AIResponseSchema(BaseModel):
    """Schema representing the standardized response returned by an AI provider."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Identifier of the model that generated the response")
    usage: Optional[AIUsageSchema] = Field(default=None, description="Token usage details")
    finish_reason: Optional[str] = Field(default=None, description="Reason why generation stopped")

