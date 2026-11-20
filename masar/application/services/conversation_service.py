"""Conversation service orchestrating multi-turn dialogues with Masar AI."""

from datetime import datetime, timezone
from typing import Optional

from masar.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from masar.application.services.ai_service import AIService
from masar.domain.exceptions.base import EmptyFieldError, InvalidIdError
from masar.domain.exceptions.conversation import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)
from masar.domain.models.ai import ChatMessage
from masar.domain.models.conversation import Conversation, ConversationMessage

DEFAULT_SYSTEM_PROMPT = (
    "You are Masar AI, an expert technical learning mentor and engineering advisor. "
    "Your mission is to help software engineers navigate complex domains, break down subjects into "
    "structured learning roadmaps, clarify conceptual doubts, and track practical progress. "
    "Be direct, insightful, and encourage structured, deliberate practice."
)


class ConversationService:
    """Coordinates conversational workflows, message persistence, and AI responses."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        ai_service: AIService,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self._repo = conversation_repository
        self._ai = ai_service
        self._system_prompt = system_prompt

    def create_conversation(
        self, user_id: int, title: Optional[str] = None
    ) -> Conversation:
        """Create and persist a new conversation for an authenticated user."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        resolved_title = title.strip() if title and title.strip() else "New Conversation"
        conv = Conversation(user_id=user_id, title=resolved_title)
        return self._repo.add_conversation(conv)

    def list_conversations(self, user_id: int) -> list[Conversation]:
        """List all conversations for a specific user ordered by latest activity."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        return self._repo.get_conversations_by_user_id(user_id)

    def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> tuple[Conversation, list[ConversationMessage]]:
        """Retrieve a conversation and its messages, enforcing user ownership."""
        conv = self._verify_ownership(conversation_id, user_id)
        messages = self._repo.get_messages_by_conversation_id(conversation_id)
        return conv, messages

    def update_title(
        self, conversation_id: int, user_id: int, title: str
    ) -> Conversation:
        """Update a conversation's title."""
        conv = self._verify_ownership(conversation_id, user_id)
        conv.update_title(title)
        return self._repo.update_conversation(conv)

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and its associated messages."""
        self._verify_ownership(conversation_id, user_id)
        return self._repo.delete_conversation(conversation_id)

    def send_message(
        self, conversation_id: int, user_id: int, content: str
    ) -> tuple[ConversationMessage, ConversationMessage]:
        """Record user message, dispatch multi-turn dialogue to AI, and persist response."""
        conv = self._verify_ownership(conversation_id, user_id)

        if not content or not content.strip():
            raise EmptyFieldError("Message content cannot be empty.")
        clean_content = content.strip()

        # 1. Persist the user's incoming message
        user_msg = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=clean_content,
        )
        saved_user_msg = self._repo.add_message(user_msg)

        # 2. Automatically generate title if still default
        if conv.title == "New Conversation":
            first_line = clean_content.split("\n")[0][:45].strip()
            new_title = f"{first_line}..." if len(clean_content) > 45 else first_line
            conv.update_title(new_title or "Learning Chat")
            self._repo.update_conversation(conv)

        # 3. Retrieve conversation history for multi-turn context
        all_messages = self._repo.get_messages_by_conversation_id(conversation_id)

        # 4. Construct ChatMessage dialogue with system instructions
        dialogue: list[ChatMessage] = [
            ChatMessage(role="system", content=self._system_prompt)
        ]
        for m in all_messages:
            dialogue.append(ChatMessage(role=m.role, content=m.content))

        # 5. Call AI Service
        ai_response = self._ai.chat(messages=dialogue)

        # 6. Persist assistant reply
        assistant_msg = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response.content,
        )
        saved_assistant_msg = self._repo.add_message(assistant_msg)

        # 7. Bump conversation updated_at
        conv.updated_at = datetime.now(timezone.utc)
        self._repo.update_conversation(conv)

        return saved_user_msg, saved_assistant_msg

    def _verify_ownership(self, conversation_id: int, user_id: int) -> Conversation:
        """Ensure the conversation exists and belongs to the requested user."""
        if conversation_id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        conv = self._repo.get_conversation_by_id(conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found."
            )
        if conv.user_id != user_id:
            raise ConversationAccessDeniedError(
                f"User {user_id} does not have access to conversation {conversation_id}."
            )
        return conv
