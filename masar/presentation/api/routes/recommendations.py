"""FastAPI route handlers for adaptive learning recommendations and knowledge gap detection."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from pydantic import BaseModel, Field

from masar.application.schemas.recommendation import (
    AdaptiveLearningSummarySchema,
    RecommendationSchema,
)
from masar.application.services.recommendation_service import RecommendationService
from masar.domain.models import User
from masar.presentation.api.dependencies import (
    get_current_user,
    get_recommendation_service,
)

router = APIRouter(prefix="/recommendations", tags=["Adaptive Learning Recommendations"])


class JourneyImprovementRequestSchema(BaseModel):
    """Schema for requesting targeted improvements to a specific journey."""

    feedback: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="User feedback, difficulty, or requested focus area",
    )


@router.get(
    "",
    response_model=AdaptiveLearningSummarySchema,
    status_code=status.HTTP_200_OK,
    summary="Get adaptive learning recommendations and knowledge gaps",
)
def get_adaptive_recommendations(
    recommendation_service: Annotated[
        RecommendationService, Depends(get_recommendation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    journey_id: Optional[int] = Query(
        default=None, ge=1, description="Optional journey ID to filter recommendations"
    ),
) -> AdaptiveLearningSummarySchema:
    """Analyze the user's journeys, progress, and knowledge profile to suggest next steps."""
    summary = recommendation_service.get_recommendations(
        user_id=current_user.id or 1,
        journey_id=journey_id,
    )
    return AdaptiveLearningSummarySchema.model_validate(summary)


@router.post(
    "/improve/{journey_id}",
    response_model=list[RecommendationSchema],
    status_code=status.HTTP_200_OK,
    summary="Propose roadmap improvements for an existing journey based on user feedback",
)
def propose_journey_improvements(
    payload: JourneyImprovementRequestSchema,
    recommendation_service: Annotated[
        RecommendationService, Depends(get_recommendation_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    journey_id: int = Path(..., ge=1, description="ID of the journey to improve"),
) -> list[RecommendationSchema]:
    """Suggest targeted new topics or updates to an existing journey based on user difficulty."""
    improvements = recommendation_service.propose_journey_improvement(
        user_id=current_user.id or 1,
        journey_id=journey_id,
        feedback=payload.feedback,
    )
    return [RecommendationSchema.model_validate(r) for r in improvements]
