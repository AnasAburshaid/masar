"""Pydantic validation schemas for Conversations and Messages."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from masar.application.schemas.action import ActionProposalResponseSchema


class ConversationCreateSchema(BaseModel):
    """Schema for creating a new conversation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Optional initial title for the conversation",
    )


class ConversationUpdateSchema(BaseModel):
    """Schema for updating a conversation's title."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Updated conversation title",
    )


class MessageCreateSchema(BaseModel):
    """Schema for sending a new message in a conversation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    content: str = Field(
        ...,
        min_length=1,
        description="Text content of the message",
    )


class MessageResponseSchema(BaseModel):
    """Schema representing an individual message in API responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class ConversationResponseSchema(BaseModel):
    """Schema representing conversation metadata in API list responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponseSchema(ConversationResponseSchema):
    """Schema representing full conversation details including messages."""

    messages: list[MessageResponseSchema] = Field(default_factory=list)
    proposals: list[ActionProposalResponseSchema] = Field(default_factory=list)


class SendMessageResponseSchema(BaseModel):
    """Schema returned after a user sends a message and the AI responds."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    user_message: MessageResponseSchema
    assistant_message: MessageResponseSchema
    action_proposal: Optional[ActionProposalResponseSchema] = None
