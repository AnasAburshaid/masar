"""FastAPI dependency injection providers for application services and settings."""

from typing import Annotated, cast
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from masar.application.services import (
    ActionService,
    AIService,
    ConversationService,
    DocumentService,
    JourneyService,
    NoteService,
    ProfileService,
    ProgressService,
    RecommendationService,
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


def get_ai_service(request: Request) -> AIService:
    """Dependency provider for AIService."""
    if hasattr(request.app.state, "ai_service") and request.app.state.ai_service is not None:
        return request.app.state.ai_service  # type: ignore[no-any-return]
    from masar.container import build_ai_service

    settings = get_app_settings(request)
    service = build_ai_service(settings=settings)
    request.app.state.ai_service = service
    return service


def get_conversation_service(request: Request) -> ConversationService:
    """Dependency provider for ConversationService."""
    if (
        hasattr(request.app.state, "conversation_service")
        and request.app.state.conversation_service is not None
    ):
        return request.app.state.conversation_service  # type: ignore[no-any-return]
    from masar.application.services.tool_registry import ServicesBundle
    from masar.container import build_conversation_service

    settings = get_app_settings(request)
    services_tuple = get_services(request)
    bundle = ServicesBundle(
        journey_service=services_tuple[0],
        section_service=services_tuple[1],
        topic_service=services_tuple[2],
        note_service=services_tuple[3],
        progress_service=services_tuple[4],
    )
    service = build_conversation_service(settings=settings, services_bundle=bundle)
    request.app.state.conversation_service = service
    return service


def get_action_service(request: Request) -> ActionService:
    """Dependency provider for ActionService."""
    if (
        hasattr(request.app.state, "action_service")
        and request.app.state.action_service is not None
    ):
        return request.app.state.action_service  # type: ignore[no-any-return]
    from masar.container import build_action_service

    settings = get_app_settings(request)
    service = build_action_service(settings=settings)
    request.app.state.action_service = service
    return service


def get_document_service(request: Request) -> DocumentService:
    """Dependency provider for DocumentService."""
    if (
        hasattr(request.app.state, "document_service")
        and request.app.state.document_service is not None
    ):
        return cast(DocumentService, request.app.state.document_service)
    from masar.container import build_document_service

    settings = get_app_settings(request)
    service = build_document_service(settings=settings)
    request.app.state.document_service = service
    return service


def get_profile_service(request: Request) -> ProfileService:
    """Dependency provider for ProfileService."""
    if (
        hasattr(request.app.state, "profile_service")
        and request.app.state.profile_service is not None
    ):
        return cast(ProfileService, request.app.state.profile_service)
    from masar.container import build_profile_service

    settings = get_app_settings(request)
    doc_service = get_document_service(request)
    ai_service = get_ai_service(request)
    service = build_profile_service(
        settings=settings,
        ai_service=ai_service,
        document_repository=doc_service._repo,
    )
    request.app.state.profile_service = service
    return service


def get_recommendation_service(request: Request) -> RecommendationService:
    """Dependency provider for RecommendationService."""
    if (
        hasattr(request.app.state, "recommendation_service")
        and request.app.state.recommendation_service is not None
    ):
        return cast(RecommendationService, request.app.state.recommendation_service)
    from masar.application.services.tool_registry import ServicesBundle
    from masar.container import build_recommendation_service

    settings = get_app_settings(request)
    services_tuple = get_services(request)
    bundle = ServicesBundle(
        journey_service=services_tuple[0],
        section_service=services_tuple[1],
        topic_service=services_tuple[2],
        note_service=services_tuple[3],
        progress_service=services_tuple[4],
    )
    ai_service = get_ai_service(request)
    profile_service = get_profile_service(request)
    service = build_recommendation_service(
        settings=settings,
        ai_service=ai_service,
        services_bundle=bundle,
        profile_service=profile_service,
    )
    request.app.state.recommendation_service = service
    return service





def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> User:
    """Dependency provider retrieving the currently authenticated User."""
    if credentials and credentials.credentials:
        try:
            return user_service.get_user_from_token(credentials.credentials)
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    if settings.environment == "testing" and not settings.strict_auth:
        default_email = "testrunner@masar.local"
        try:
            return user_service.get_user_by_email(default_email)
        except Exception:
            return user_service.register_user(default_email, "TestPassword123!")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
