"""In-memory implementation of ConversationRepository for rapid testing."""

from masar.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from masar.domain.models.conversation import Conversation, ConversationMessage


class InMemoryConversationRepository(ConversationRepository):
    """In-memory storage implementation for Conversations and Messages."""

    def __init__(self) -> None:
        self._conversations: dict[int, Conversation] = {}
        self._messages: dict[int, list[ConversationMessage]] = {}
        self._next_conv_id: int = 1
        self._next_msg_id: int = 1

    def add_conversation(self, conversation: Conversation) -> Conversation:
        if conversation.id is None:
            conversation.id = self._next_conv_id
            self._next_conv_id += 1
        self._conversations[conversation.id] = conversation
        if conversation.id not in self._messages:
            self._messages[conversation.id] = []
        return conversation

    def get_conversation_by_id(self, conversation_id: int) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def get_conversations_by_user_id(self, user_id: int) -> list[Conversation]:
        convs = [c for c in self._conversations.values() if c.user_id == user_id]
        return sorted(convs, key=lambda c: (c.updated_at, c.id or 0), reverse=True)

    def update_conversation(self, conversation: Conversation) -> Conversation:
        if conversation.id is None or conversation.id not in self._conversations:
            raise ValueError(f"Conversation {conversation.id} was not found.")
        self._conversations[conversation.id] = conversation
        return conversation

    def delete_conversation(self, conversation_id: int) -> bool:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            self._messages.pop(conversation_id, None)
            return True
        return False

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        if message.id is None:
            message.id = self._next_msg_id
            self._next_msg_id += 1
        if message.conversation_id not in self._messages:
            self._messages[message.conversation_id] = []
        self._messages[message.conversation_id].append(message)
        return message

    def get_messages_by_conversation_id(
        self, conversation_id: int
    ) -> list[ConversationMessage]:
        msgs = self._messages.get(conversation_id, [])
        return sorted(msgs, key=lambda m: (m.created_at, m.id or 0))
