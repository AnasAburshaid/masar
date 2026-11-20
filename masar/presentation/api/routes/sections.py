"""Section endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, status

from masar.application.schemas.section import (
    SectionCreateSchema,
    SectionResponseSchema,
    SectionUpdateSchema,
)
from masar.application.services import SectionService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_section_service

router = APIRouter(tags=["Sections"])


@router.post(
    "/sections",
    response_model=SectionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new section in a journey",
)
def create_section(
    payload: SectionCreateSchema,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionResponseSchema:
    """Create a new learning section within an existing journey owned by user."""
    section = section_service.create_section(
        journey_id=payload.journey_id,
        title=payload.title,
        user_id=current_user.id,
    )
    return SectionResponseSchema.model_validate(section)


@router.get(
    "/sections/{section_id}",
    response_model=SectionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get section by ID",
)
def get_section(
    section_id: Annotated[int, Path(..., gt=0, description="The positive ID of the section to retrieve")],
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionResponseSchema:
    """Retrieve details of a single section."""
    section = section_service.get_section(section_id, user_id=current_user.id)
    return SectionResponseSchema.model_validate(section)


@router.get(
    "/journeys/{journey_id}/sections",
    response_model=list[SectionResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List sections for a journey",
)
def list_sections_by_journey_path(
    journey_id: Annotated[int, Path(..., gt=0, description="Journey ID whose sections to list")],
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SectionResponseSchema]:
    """Retrieve all sections belonging to a specific learning journey."""
    sections = section_service.list_sections(journey_id, user_id=current_user.id)
    return [SectionResponseSchema.model_validate(s) for s in sections]


@router.get(
    "/sections",
    response_model=list[SectionResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List sections by journey ID query",
)
def list_sections_by_journey_query(
    journey_id: Annotated[int, Query(..., gt=0, description="Journey ID whose sections to list")],
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SectionResponseSchema]:
    """Retrieve all sections belonging to a specific learning journey."""
    sections = section_service.list_sections(journey_id, user_id=current_user.id)
    return [SectionResponseSchema.model_validate(s) for s in sections]


@router.put(
    "/sections/{section_id}",
    response_model=SectionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update section title",
)
@router.patch(
    "/sections/{section_id}",
    response_model=SectionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Partially update section",
)
def update_section(
    section_id: Annotated[int, Path(..., gt=0, description="The positive ID of the section to update")],
    payload: SectionUpdateSchema,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionResponseSchema:
    """Rename an existing section."""
    existing = section_service.get_section(section_id, user_id=current_user.id)
    new_title = payload.title if payload.title is not None else existing.title
    updated = section_service.rename_section(section_id, new_title, user_id=current_user.id)
    return SectionResponseSchema.model_validate(updated)


@router.delete(
    "/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete section",
)
def delete_section(
    section_id: Annotated[int, Path(..., gt=0, description="The positive ID of the section to delete")],
    section_service: Annotated[SectionService, Depends(get_section_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a section and cascade delete all its topics and notes."""
    section_service.delete_section(section_id, user_id=current_user.id)
