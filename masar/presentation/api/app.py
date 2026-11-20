"""FastAPI application factory and configuration for Masar."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from masar.config.settings import Settings, get_settings
from masar.domain.exceptions import (
    AccessDeniedError,
    AuthenticationError,
    EntityNotFoundError,
    StorageError,
    UserAlreadyExistsError,
    ValidationError,
)
from masar.presentation.api.routes.auth import router as auth_router
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

    # Attach settings and application services to app state
    from masar.container import build_container, build_user_service

    app.state.settings = active_settings
    app.state.services = build_container(settings=active_settings)
    app.state.user_service = build_user_service(settings=active_settings)

    # Include routers
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(journeys_router)
    app.include_router(sections_router)
    app.include_router(topics_router)
    app.include_router(notes_router)
    app.include_router(progress_router)

    return app


# Module-level default application instance for ASGI servers
app = create_app()
