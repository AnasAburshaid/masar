"""Conversation and AI Chat endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Response, status

from masar.application.schemas.action import (
    ActionApprovalResponseSchema,
    ActionProposalResponseSchema,
)
from masar.application.schemas.conversation import (
    ConversationCreateSchema,
    ConversationDetailResponseSchema,
    ConversationResponseSchema,
    ConversationUpdateSchema,
    MessageCreateSchema,
    MessageResponseSchema,
    SendMessageResponseSchema,
)
from masar.application.services.action_service import ActionService
from masar.application.services.conversation_service import ConversationService
from masar.domain.models import User
from masar.presentation.api.dependencies import (
    get_action_service,
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
    action_service: Annotated[ActionService, Depends(get_action_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationDetailResponseSchema:
    """Retrieve a conversation by ID along with its full ordered message history and proposals."""
    conv, messages = conversation_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
    )
    proposals = action_service.list_proposals(
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
        proposals=[ActionProposalResponseSchema.model_validate(p) for p in proposals],
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
    user_msg, assistant_msg, proposal = conversation_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
        content=payload.content,
    )
    return SendMessageResponseSchema(
        user_message=MessageResponseSchema.model_validate(user_msg),
        assistant_message=MessageResponseSchema.model_validate(assistant_msg),
        action_proposal=ActionProposalResponseSchema.model_validate(proposal) if proposal else None,
    )


# -------------------------------------------------------------
# Action Proposals Endpoints
# -------------------------------------------------------------

@router.get(
    "/{conversation_id}/proposals",
    response_model=list[ActionProposalResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List action proposals for a conversation",
)
def list_proposals(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    action_service: Annotated[ActionService, Depends(get_action_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ActionProposalResponseSchema]:
    """Retrieve all action proposals for the specified conversation."""
    proposals = action_service.list_proposals(
        conversation_id=conversation_id,
        user_id=current_user.id or 1,
    )
    return [ActionProposalResponseSchema.model_validate(p) for p in proposals]


@router.get(
    "/{conversation_id}/proposals/{proposal_id}",
    response_model=ActionProposalResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific action proposal",
)
def get_proposal(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    proposal_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the proposal"),
    ],
    action_service: Annotated[ActionService, Depends(get_action_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ActionProposalResponseSchema:
    """Retrieve an action proposal by ID."""
    proposal = action_service.get_proposal(
        proposal_id=proposal_id,
        user_id=current_user.id or 1,
    )
    return ActionProposalResponseSchema.model_validate(proposal)


@router.post(
    "/{conversation_id}/proposals/{proposal_id}/approve",
    response_model=ActionApprovalResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Approve and execute a proposed action plan",
)
def approve_proposal(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    proposal_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the proposal"),
    ],
    action_service: Annotated[ActionService, Depends(get_action_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ActionApprovalResponseSchema:
    """Approve a pending action proposal and execute its tools sequentially."""
    updated_proposal, results = action_service.approve_and_execute_proposal(
        proposal_id=proposal_id,
        user_id=current_user.id or 1,
    )
    executed_count = sum(1 for r in results if r.status == "success")
    failed_count = sum(1 for r in results if r.status == "failure")

    status_msg = (
        f"Proposal executed successfully: {executed_count} actions completed."
        if failed_count == 0
        else f"Proposal execution halted: {executed_count} completed, {failed_count} failed."
    )

    return ActionApprovalResponseSchema(
        proposal=ActionProposalResponseSchema.model_validate(updated_proposal),
        message=status_msg,
        executed_count=executed_count,
        failed_count=failed_count,
    )


@router.post(
    "/{conversation_id}/proposals/{proposal_id}/reject",
    response_model=ActionProposalResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Reject a proposed action plan",
)
def reject_proposal(
    conversation_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the conversation"),
    ],
    proposal_id: Annotated[
        int,
        Path(..., gt=0, description="The positive integer ID of the proposal"),
    ],
    action_service: Annotated[ActionService, Depends(get_action_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ActionProposalResponseSchema:
    """Reject a pending action proposal."""
    rejected = action_service.reject_proposal(
        proposal_id=proposal_id,
        user_id=current_user.id or 1,
    )
    return ActionProposalResponseSchema.model_validate(rejected)
