"""Journey endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, status

from masar.application.schemas.journey import (
    JourneyCreateSchema,
    JourneyResponseSchema,
    JourneyUpdateSchema,
)
from masar.application.services import JourneyService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_journey_service

router = APIRouter(prefix="/journeys", tags=["Journeys"])


@router.post(
    "",
    response_model=JourneyResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new learning journey",
)
def create_journey(
    payload: JourneyCreateSchema,
    journey_service: Annotated[JourneyService, Depends(get_journey_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> JourneyResponseSchema:
    """Create a new learning journey associated with the authenticated user."""
    journey = journey_service.create_journey(
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
    )
    return JourneyResponseSchema.model_validate(journey)


@router.get(
    "",
    response_model=list[JourneyResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List all learning journeys for current user",
)
def list_journeys(
    journey_service: Annotated[JourneyService, Depends(get_journey_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[JourneyResponseSchema]:
    """Retrieve learning journeys owned by the authenticated user."""
    journeys = journey_service.list_journeys(user_id=current_user.id)
    return [JourneyResponseSchema.model_validate(j) for j in journeys]


@router.get(
    "/{journey_id}",
    response_model=JourneyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get a learning journey by ID",
)
def get_journey(
    journey_id: Annotated[int, Path(..., gt=0, description="The positive ID of the journey to retrieve")],
    journey_service: Annotated[JourneyService, Depends(get_journey_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> JourneyResponseSchema:
    """Retrieve a single learning journey by its unique identifier."""
    journey = journey_service.get_journey(journey_id, user_id=current_user.id)
    return JourneyResponseSchema.model_validate(journey)


@router.put(
    "/{journey_id}",
    response_model=JourneyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update a learning journey",
)
@router.patch(
    "/{journey_id}",
    response_model=JourneyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Partially update a learning journey",
)
def update_journey(
    journey_id: Annotated[int, Path(..., gt=0, description="The positive ID of the journey to update")],
    payload: JourneyUpdateSchema,
    journey_service: Annotated[JourneyService, Depends(get_journey_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> JourneyResponseSchema:
    """Update title and/or description of an existing learning journey."""
    existing = journey_service.get_journey(journey_id, user_id=current_user.id)
    new_title = payload.title if payload.title is not None else existing.title
    new_description = payload.description if payload.description is not None else existing.description
    updated = journey_service.update_journey(
        journey_id,
        title=new_title,
        description=new_description,
        user_id=current_user.id,
    )
    return JourneyResponseSchema.model_validate(updated)


@router.delete(
    "/{journey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a learning journey",
)
def delete_journey(
    journey_id: Annotated[int, Path(..., gt=0, description="The positive ID of the journey to delete")],
    journey_service: Annotated[JourneyService, Depends(get_journey_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a learning journey and cascade delete its sections, topics, and notes."""
    journey_service.delete_journey(journey_id, user_id=current_user.id)
