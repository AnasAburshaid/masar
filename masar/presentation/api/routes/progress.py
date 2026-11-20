"""Progress endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, status

from masar.application.schemas.progress import (
    JourneyProgressSchema,
    SectionProgressSchema,
)
from masar.application.services import ProgressService, SectionService
from masar.domain.models import User
from masar.presentation.api.dependencies import (
    get_current_user,
    get_progress_service,
    get_section_service,
)

router = APIRouter(tags=["Progress"])


@router.get(
    "/journeys/{journey_id}/progress",
    response_model=JourneyProgressSchema,
    status_code=status.HTTP_200_OK,
    summary="Get learning progress for a journey",
)
def get_journey_progress(
    journey_id: Annotated[int, Path(..., gt=0, description="The positive ID of the journey")],
    progress_service: Annotated[ProgressService, Depends(get_progress_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> JourneyProgressSchema:
    """Retrieve overall learning progress and per-section progress breakdown for a journey."""
    journey, overall, section_breakdown = progress_service.calculate_journey_detailed_progress(
        journey_id, user_id=current_user.id
    )

    sections_schema = [
        SectionProgressSchema(
            section_id=section.id or 0,
            title=section.title,
            completed_topics=prog.completed_topics,
            total_topics=prog.total_topics,
            percentage=prog.percentage,
            is_complete=prog.is_complete,
        )
        for section, prog in section_breakdown
    ]

    return JourneyProgressSchema(
        journey_id=journey_id,
        title=journey.title,
        completed_topics=overall.completed_topics,
        total_topics=overall.total_topics,
        percentage=overall.percentage,
        is_complete=overall.is_complete,
        sections=sections_schema,
    )


@router.get(
    "/sections/{section_id}/progress",
    response_model=SectionProgressSchema,
    status_code=status.HTTP_200_OK,
    summary="Get learning progress for a section",
)
def get_section_progress(
    section_id: Annotated[int, Path(..., gt=0, description="The positive ID of the section")],
    section_service: Annotated[SectionService, Depends(get_section_service)],
    progress_service: Annotated[ProgressService, Depends(get_progress_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionProgressSchema:
    """Retrieve learning progress for a specific section."""
    section = section_service.get_section(section_id, user_id=current_user.id)
    prog = progress_service.calculate_section_progress(section_id, user_id=current_user.id)

    return SectionProgressSchema(
        section_id=section_id,
        title=section.title,
        completed_topics=prog.completed_topics,
        total_topics=prog.total_topics,
        percentage=prog.percentage,
        is_complete=prog.is_complete,
    )
