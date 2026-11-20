"""FastAPI application factory and configuration for Masar."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from masar.config.settings import Settings, get_settings
from masar.domain.exceptions import (
    AccessDeniedError,
    AIAuthenticationError,
    AIConfigurationError,
    AIError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AuthenticationError,
    DocumentAccessDeniedError,
    DocumentError,
    DocumentExtractionError,
    DocumentNotFoundError,
    EmptyDocumentError,
    EntityNotFoundError,
    FileTooLargeError,
    StorageError,
    UnsupportedFileTypeError,
    UserAlreadyExistsError,
    ValidationError,
)
from masar.presentation.api.routes.auth import router as auth_router
from masar.presentation.api.routes.conversations import router as conversations_router
from masar.presentation.api.routes.documents import router as documents_router
from masar.presentation.api.routes.journeys import router as journeys_router
from masar.presentation.api.routes.notes import router as notes_router
from masar.presentation.api.routes.progress import router as progress_router
from masar.presentation.api.routes.root import router as root_router
from masar.presentation.api.routes.sections import router as sections_router
from masar.presentation.api.routes.topics import router as topics_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create, configure, and wire the FastAPI application instance."""
    active_settings = settings or get_settings()

    app = FastAPI(
        title=active_settings.app_name,
        description="Developer Learning Tracker - REST API and Interactive Documentation",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register domain exception handlers
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(StorageError)
    async def storage_error_handler(request: Request, exc: StorageError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Storage Error: {exc}"},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AccessDeniedError)
    async def access_denied_handler(request: Request, exc: AccessDeniedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIAuthenticationError)
    async def ai_auth_error_handler(request: Request, exc: AIAuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIRateLimitError)
    async def ai_rate_limit_handler(request: Request, exc: AIRateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AITimeoutError)
    async def ai_timeout_handler(request: Request, exc: AITimeoutError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIConfigurationError)
    async def ai_configuration_handler(request: Request, exc: AIConfigurationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIProviderError)
    async def ai_provider_error_handler(request: Request, exc: AIProviderError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIError)
    async def ai_error_handler(request: Request, exc: AIError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentAccessDeniedError)
    async def document_access_denied_handler(request: Request, exc: DocumentAccessDeniedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(request: Request, exc: FileTooLargeError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_file_type_handler(request: Request, exc: UnsupportedFileTypeError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentExtractionError)
    async def document_extraction_handler(request: Request, exc: DocumentExtractionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(EmptyDocumentError)
    async def empty_document_handler(request: Request, exc: EmptyDocumentError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentError)
    async def document_error_handler(request: Request, exc: DocumentError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    # Attach settings and application services to app state
    from masar.application.services.tool_registry import ServicesBundle
    from masar.container import (
        build_action_service,
        build_ai_service,
        build_container,
        build_conversation_service,
        build_document_service,
        build_user_service,
    )

    app.state.settings = active_settings
    services_tuple = build_container(settings=active_settings)
    app.state.services = services_tuple
    app.state.user_service = build_user_service(settings=active_settings)
    ai_service = build_ai_service(settings=active_settings)
    app.state.ai_service = ai_service

    document_service = build_document_service(
        settings=active_settings, ai_service=ai_service
    )
    app.state.document_service = document_service

    bundle = ServicesBundle(
        journey_service=services_tuple[0],
        section_service=services_tuple[1],
        topic_service=services_tuple[2],
        note_service=services_tuple[3],
        progress_service=services_tuple[4],
    )
    action_service = build_action_service(
        settings=active_settings, services_bundle=bundle
    )
    app.state.action_service = action_service

    app.state.conversation_service = build_conversation_service(
        settings=active_settings,
        ai_service=ai_service,
        action_service=action_service,
        services_bundle=bundle,
        document_repository=document_service._repo,
    )

    # Include routers
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(conversations_router)
    app.include_router(documents_router)
    app.include_router(journeys_router)
    app.include_router(sections_router)
    app.include_router(topics_router)
    app.include_router(notes_router)
    app.include_router(progress_router)

    return app


# Module-level default application instance for ASGI servers
app = create_app()
