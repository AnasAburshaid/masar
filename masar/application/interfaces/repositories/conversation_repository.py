"""Conversation repository abstraction."""

from abc import ABC, abstractmethod

from masar.domain.models.conversation import Conversation, ConversationMessage


class ConversationRepository(ABC):
    """Abstract repository interface for Conversations and Messages."""

    @abstractmethod
    def add_conversation(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation."""

    @abstractmethod
    def get_conversation_by_id(self, conversation_id: int) -> Conversation | None:
        """Retrieve a conversation by its unique identifier."""

    @abstractmethod
    def get_conversations_by_user_id(self, user_id: int) -> list[Conversation]:
        """Retrieve all conversations belonging to a specific user, ordered by recent activity."""

    @abstractmethod
    def update_conversation(self, conversation: Conversation) -> Conversation:
        """Update conversation metadata (e.g., title, updated_at)."""

    @abstractmethod
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and its cascaded messages. Returns True if deleted."""

    @abstractmethod
    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        """Persist an individual message within a conversation."""

    @abstractmethod
    def get_messages_by_conversation_id(
        self, conversation_id: int
    ) -> list[ConversationMessage]:
        """Retrieve all messages for a conversation ordered chronologically."""
