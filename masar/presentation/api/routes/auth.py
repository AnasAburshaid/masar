"""Authentication and user management endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, status

from masar.application.schemas.user import (
    UserRegisterSchema,
    UserResponseSchema,
)
from masar.application.services import UserService
from masar.presentation.api.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    payload: UserRegisterSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponseSchema:
    """Register a new user with email and secure password."""
    user = user_service.register_user(
        email=payload.email,
        password=payload.password,
    )
    return UserResponseSchema.model_validate(user)
