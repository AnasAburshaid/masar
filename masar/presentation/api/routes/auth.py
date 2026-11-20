"""Authentication and user management endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, status

from masar.application.schemas.token import (
    LoginRequestSchema,
    TokenResponseSchema,
)
from masar.application.schemas.user import (
    UserRegisterSchema,
    UserResponseSchema,
)
from masar.application.services import UserService
from masar.domain.models import User
from masar.presentation.api.dependencies import (
    get_current_user,
    get_user_service,
)

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


@router.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Log in and obtain a JWT access token",
)
def login(
    payload: LoginRequestSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponseSchema:
    """Authenticate with email and password to receive a JWT access token."""
    _, token = user_service.login_user(
        email=payload.email,
        password=payload.password,
    )
    return TokenResponseSchema(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponseSchema:
    """Return profile information of the currently authenticated user."""
    return UserResponseSchema.model_validate(current_user)
