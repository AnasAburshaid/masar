"""FastAPI route handlers for user learning knowledge profile management and AI extraction."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Response, status

from masar.application.schemas.profile import (
    LearningProfileResponseSchema,
    ProfileBioUpdateSchema,
    ProfileExtractionResponseSchema,
    ProfileItemCreateSchema,
    ProfileItemSchema,
    ProfileItemUpdateSchema,
)
from masar.application.services.profile_service import ProfileService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_profile_service

router = APIRouter(prefix="/profile", tags=["Learning Profile"])


@router.get(
    "",
    response_model=LearningProfileResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user's complete learning profile",
)
def get_user_profile(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LearningProfileResponseSchema:
    """Get the authenticated user's confirmed and AI-inferred learning profile."""
    profile = profile_service.get_profile(user_id=current_user.id or 1)
    return LearningProfileResponseSchema.model_validate(profile)


@router.put(
    "/bio",
    response_model=LearningProfileResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update user's professional bio",
)
def update_profile_bio(
    payload: ProfileBioUpdateSchema,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LearningProfileResponseSchema:
    """Update high-level background / bio in the user's profile."""
    profile_service.update_bio(user_id=current_user.id or 1, bio=payload.bio)
    profile = profile_service.get_profile(user_id=current_user.id or 1)
    return LearningProfileResponseSchema.model_validate(profile)


@router.post(
    "/items",
    response_model=ProfileItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new profile item (skill, tech, language, project, or goal)",
)
def add_profile_item(
    payload: ProfileItemCreateSchema,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileItemSchema:
    """Add a skill, technology, language, experience, project, knowledge, or goal item."""
    item = profile_service.add_item(
        user_id=current_user.id or 1,
        name=payload.name,
        category=payload.category,
        level=payload.level,
        is_confirmed=payload.is_confirmed,
        source_type="manual",
    )
    return ProfileItemSchema.model_validate(item)


@router.put(
    "/items/{item_id}",
    response_model=ProfileItemSchema,
    status_code=status.HTTP_200_OK,
    summary="Update an existing profile item",
)
def update_profile_item(
    payload: ProfileItemUpdateSchema,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., ge=1, description="ID of the profile item"),
) -> ProfileItemSchema:
    """Modify name, level, category, or confirmation status of a profile item."""
    item = profile_service.update_item(
        user_id=current_user.id or 1,
        item_id=item_id,
        name=payload.name,
        category=payload.category,
        level=payload.level,
        is_confirmed=payload.is_confirmed,
    )
    return ProfileItemSchema.model_validate(item)


@router.post(
    "/items/{item_id}/confirm",
    response_model=ProfileItemSchema,
    status_code=status.HTTP_200_OK,
    summary="Confirm an AI-inferred profile item",
)
def confirm_profile_item(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., ge=1, description="ID of the profile item"),
) -> ProfileItemSchema:
    """Approve and confirm an AI-inferred skill or knowledge item."""
    item = profile_service.confirm_item(user_id=current_user.id or 1, item_id=item_id)
    return ProfileItemSchema.model_validate(item)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a profile item",
)
def delete_profile_item(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., ge=1, description="ID of the profile item"),
) -> Response:
    """Remove a profile item from user profile."""
    profile_service.delete_item(user_id=current_user.id or 1, item_id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/extract/document/{document_id}",
    response_model=ProfileExtractionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Extract profile skills and knowledge from an uploaded document",
)
def extract_profile_from_document(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    document_id: int = Path(..., ge=1, description="ID of the uploaded document"),
) -> ProfileExtractionResponseSchema:
    """Analyze a document and extract skills, experience, and goals awaiting user review."""
    items = profile_service.extract_from_document(
        user_id=current_user.id or 1,
        document_id=document_id,
    )
    return ProfileExtractionResponseSchema(
        extracted_items=[ProfileItemSchema.model_validate(i) for i in items],
        source_type="document",
        source_id=document_id,
    )
