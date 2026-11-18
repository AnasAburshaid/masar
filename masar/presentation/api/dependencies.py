"""FastAPI dependency injection providers for application services and settings."""

from typing import Annotated
from fastapi import Depends, Request

from masar.application.services import (
    JourneyService,
    NoteService,
    ProgressService,
    SectionService,
    TopicService,
)
from masar.config.settings import Settings, get_settings
from masar.container import build_container

ServicesTuple = tuple[
    JourneyService, SectionService, TopicService, NoteService, ProgressService
]


def get_app_settings(request: Request) -> Settings:
    """Retrieve settings from application state if available, else get default settings."""
    if hasattr(request.app.state, "settings") and request.app.state.settings is not None:
        return request.app.state.settings  # type: ignore[no-any-return]
    return get_settings()


def get_services(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ServicesTuple:
    """Instantiate and wire application services using the active settings."""
    return build_container(settings=settings)


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
