"""FastAPI dependency injection providers for application services and settings."""

from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from masar.application.services import (
    JourneyService,
    NoteService,
    ProgressService,
    SectionService,
    TopicService,
    UserService,
)
from masar.config.settings import Settings, get_settings
from masar.domain.exceptions import AuthenticationError
from masar.domain.models import User

ServicesTuple = tuple[
    JourneyService, SectionService, TopicService, NoteService, ProgressService
]

http_bearer_scheme = HTTPBearer(auto_error=False)


def get_app_settings(request: Request) -> Settings:
    """Retrieve settings from application state if available, else get default settings."""
    if hasattr(request.app.state, "settings") and request.app.state.settings is not None:
        return request.app.state.settings  # type: ignore[no-any-return]
    return get_settings()


def get_services(request: Request) -> ServicesTuple:
    """Retrieve or initialize shared application services from application state."""
    if hasattr(request.app.state, "services") and request.app.state.services is not None:
        return request.app.state.services  # type: ignore[no-any-return]
    from masar.container import build_container

    settings = get_app_settings(request)
    services = build_container(settings=settings)
    request.app.state.services = services
    return services


def get_journey_service(
    services: Annotated[ServicesTuple, Depends(get_services)],
) -> JourneyService:
    """Dependency provider for JourneyService."""
    return services[0]


def get_section_service(
    services: Annotated[ServicesTuple, Depends(get_services)],
) -> SectionService:
    """Dependency provider for SectionService."""
    return services[1]


def get_topic_service(
    services: Annotated[ServicesTuple, Depends(get_services)],
) -> TopicService:
    """Dependency provider for TopicService."""
    return services[2]


def get_note_service(
    services: Annotated[ServicesTuple, Depends(get_services)],
) -> NoteService:
    """Dependency provider for NoteService."""
    return services[3]


def get_progress_service(
    services: Annotated[ServicesTuple, Depends(get_services)],
) -> ProgressService:
    """Dependency provider for ProgressService."""
    return services[4]


def get_user_service(request: Request) -> UserService:
    """Dependency provider for UserService."""
    if hasattr(request.app.state, "user_service") and request.app.state.user_service is not None:
        return request.app.state.user_service  # type: ignore[no-any-return]
    from masar.container import build_user_service

    settings = get_app_settings(request)
    service = build_user_service(settings=settings)
    request.app.state.user_service = service
    return service


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Dependency provider retrieving the currently authenticated User."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return user_service.get_user_from_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
