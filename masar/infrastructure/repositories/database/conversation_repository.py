"""SQLAlchemy implementation of ConversationRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from masar.domain.models.conversation import Conversation, ConversationMessage
from masar.infrastructure.database.models import (
    ConversationMessageModel,
    ConversationModel,
)


class SqlConversationRepository(ConversationRepository):
    """SQLAlchemy implementation for Conversations and Messages."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_conversation_entity(model: ConversationModel) -> Conversation:
        return Conversation(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_message_entity(model: ConversationMessageModel) -> ConversationMessage:
        return ConversationMessage(
            id=model.id,
            conversation_id=model.conversation_id,
            role=model.role,
            content=model.content,
            created_at=model.created_at,
        )

    def add_conversation(self, conversation: Conversation) -> Conversation:
        model = ConversationModel(
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_conversation_entity(model)

    def get_conversation_by_id(self, conversation_id: int) -> Conversation | None:
        model = self._session.get(ConversationModel, conversation_id)
        return self._to_conversation_entity(model) if model else None

    def get_conversations_by_user_id(self, user_id: int) -> list[Conversation]:
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.user_id == user_id)
            .order_by(ConversationModel.updated_at.desc(), ConversationModel.id.desc())
        )
        models = self._session.scalars(stmt).all()
        return [self._to_conversation_entity(m) for m in models]

    def update_conversation(self, conversation: Conversation) -> Conversation:
        if conversation.id is None:
            raise ValueError("Cannot update conversation without an ID")
        model = self._session.get(ConversationModel, conversation.id)
        if model is None:
            raise ValueError(f"Conversation {conversation.id} not found")
        model.title = conversation.title
        model.updated_at = conversation.updated_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_conversation_entity(model)

    def delete_conversation(self, conversation_id: int) -> bool:
        model = self._session.get(ConversationModel, conversation_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        model = ConversationMessageModel(
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_message_entity(model)

    def get_messages_by_conversation_id(
        self, conversation_id: int
    ) -> list[ConversationMessage]:
        stmt = (
            select(ConversationMessageModel)
            .where(ConversationMessageModel.conversation_id == conversation_id)
            .order_by(ConversationMessageModel.created_at.asc(), ConversationMessageModel.id.asc())
        )
        models = self._session.scalars(stmt).all()
        return [self._to_message_entity(m) for m in models]
