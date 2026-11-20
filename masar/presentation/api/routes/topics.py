"""Topic endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, status

from masar.application.schemas.topic import (
    TopicCreateSchema,
    TopicResponseSchema,
    TopicUpdateSchema,
)
from masar.application.services import TopicService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_topic_service

router = APIRouter(tags=["Topics"])


@router.post(
    "/topics",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new topic in a section",
)
def create_topic(
    payload: TopicCreateSchema,
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopicResponseSchema:
    """Create a new topic inside an existing section owned by user."""
    topic = topic_service.create_topic(
        section_id=payload.section_id,
        title=payload.title,
        user_id=current_user.id,
    )
    if payload.is_completed:
        topic = topic_service.set_topic_completion(topic.id or 0, True, user_id=current_user.id)
    return TopicResponseSchema.model_validate(topic)


@router.get(
    "/topics/{topic_id}",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get topic by ID",
)
def get_topic(
    topic_id: Annotated[int, Path(..., gt=0, description="The positive ID of the topic to retrieve")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopicResponseSchema:
    """Retrieve details of a single topic."""
    topic = topic_service.get_topic(topic_id, user_id=current_user.id)
    return TopicResponseSchema.model_validate(topic)


@router.get(
    "/sections/{section_id}/topics",
    response_model=list[TopicResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List topics for a section",
)
def list_topics_by_section_path(
    section_id: Annotated[int, Path(..., gt=0, description="Section ID whose topics to list")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[TopicResponseSchema]:
    """Retrieve all topics belonging to a specific section."""
    topics = topic_service.list_topics(section_id, user_id=current_user.id)
    return [TopicResponseSchema.model_validate(t) for t in topics]


@router.get(
    "/topics",
    response_model=list[TopicResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List topics by section ID query",
)
def list_topics_by_section_query(
    section_id: Annotated[int, Query(..., gt=0, description="Section ID whose topics to list")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[TopicResponseSchema]:
    """Retrieve all topics belonging to a specific section."""
    topics = topic_service.list_topics(section_id, user_id=current_user.id)
    return [TopicResponseSchema.model_validate(t) for t in topics]


@router.put(
    "/topics/{topic_id}",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update topic title and/or completion",
)
@router.patch(
    "/topics/{topic_id}",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Partially update topic",
)
def update_topic(
    topic_id: Annotated[int, Path(..., gt=0, description="The positive ID of the topic to update")],
    payload: TopicUpdateSchema,
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopicResponseSchema:
    """Update topic title and/or completion status."""
    topic = topic_service.get_topic(topic_id, user_id=current_user.id)
    if payload.title is not None:
        topic = topic_service.rename_topic(topic_id, payload.title, user_id=current_user.id)
    if payload.is_completed is not None:
        topic = topic_service.set_topic_completion(topic_id, payload.is_completed, user_id=current_user.id)
    return TopicResponseSchema.model_validate(topic)


@router.patch(
    "/topics/{topic_id}/complete",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Mark topic as completed",
)
def mark_topic_completed(
    topic_id: Annotated[int, Path(..., gt=0, description="The positive ID of the topic to complete")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopicResponseSchema:
    """Mark a topic as completed."""
    topic = topic_service.set_topic_completion(topic_id, True, user_id=current_user.id)
    return TopicResponseSchema.model_validate(topic)


@router.patch(
    "/topics/{topic_id}/pending",
    response_model=TopicResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Mark topic as pending",
)
def mark_topic_pending(
    topic_id: Annotated[int, Path(..., gt=0, description="The positive ID of the topic to mark pending")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopicResponseSchema:
    """Mark a topic as pending (incomplete)."""
    topic = topic_service.set_topic_completion(topic_id, False, user_id=current_user.id)
    return TopicResponseSchema.model_validate(topic)


@router.delete(
    "/topics/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete topic",
)
def delete_topic(
    topic_id: Annotated[int, Path(..., gt=0, description="The positive ID of the topic to delete")],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a topic and cascade delete all its attached notes."""
    topic_service.delete_topic(topic_id, user_id=current_user.id)
