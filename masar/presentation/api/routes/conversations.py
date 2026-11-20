"""Conversation and AI Chat endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Response, status

from masar.application.schemas.conversation import (
    ConversationCreateSchema,
    ConversationDetailResponseSchema,
    ConversationResponseSchema,
    ConversationUpdateSchema,
    MessageCreateSchema,
    MessageResponseSchema,
    SendMessageResponseSchema,
)
from masar.application.services.conversation_service import ConversationService
from masar.domain.models import User
from masar.presentation.api.dependencies import (
    get_conversation_service,
    get_current_user,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post(
    "",
    response_model=ConversationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation thread",
)
def create_conversation(
    payload: ConversationCreateSchema,
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationResponseSchema:
    """Create a new conversational dialogue thread for the authenticated user."""
    conv = conversation_service.create_conversation(
        user_id=current_user.id or 1,
        title=payload.title,
    )
    return ConversationResponseSchema.model_validate(conv)


@router.get(
    "",
    response_model=list[ConversationResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List all conversations for current user",
)
def list_conversations(
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ConversationResponseSchema]:
    """Retrieve all conversations belonging to the authenticated user ordered by recent activity."""
    convs = conversation_service.list_conversations(user_id=current_user.id or 1)
    return [ConversationResponseSchema.model_validate(c) for c in convs]


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get conversation details and full message history",
)
def get_conversation(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationDetailResponseSchema:
    """Retrieve a conversation by ID along with its full ordered message history."""
    conv, messages = conversation_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
    )
    return ConversationDetailResponseSchema(
        id=conv.id or conversation_id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponseSchema.model_validate(m) for m in messages],
    )


@router.put(
    "/{conversation_id}",
    response_model=ConversationResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update conversation title",
)
def update_conversation(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    payload: ConversationUpdateSchema,
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationResponseSchema:
    """Update the title of an existing conversation."""
    conv = conversation_service.update_title(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
        title=payload.title,
    )
    return ConversationResponseSchema.model_validate(conv)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation and its messages",
)
def delete_conversation(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Delete a conversation thread and all cascaded messages."""
    conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{conversation_id}/messages",
    response_model=SendMessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to Masar AI and receive a response",
)
def send_message(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    payload: MessageCreateSchema,
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SendMessageResponseSchema:
    """Send a user message in an existing conversation and receive the AI assistant's response."""
    user_msg, assistant_msg = conversation_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
        content=payload.content,
    )
    return SendMessageResponseSchema(
        user_message=MessageResponseSchema.model_validate(user_msg),
        assistant_message=MessageResponseSchema.model_validate(assistant_msg),
    )
