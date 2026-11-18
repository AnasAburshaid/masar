"""Root and health check endpoints for Masar API."""

from typing import Annotated, Any
from fastapi import APIRouter, Depends

from masar.config.settings import Settings
from masar.presentation.api.dependencies import get_app_settings

router = APIRouter(tags=["General"])


@router.get("/", summary="Root API Information")
def read_root(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> dict[str, Any]:
    """Return welcome message, application metadata, and links to documentation."""
    return {
        "message": "Welcome to Masar API",
        "app_name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.environment,
        "docs_url": "/docs",
        "health_url": "/health",
    }


@router.get("/health", summary="Application Health Check")
def check_health(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> dict[str, str]:
    """Return runtime health status and persistence mode."""
    return {
        "status": "ok",
        "environment": settings.environment,
        "storage_type": settings.storage_type,
    }
