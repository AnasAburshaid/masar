"""API route packages."""

from masar.presentation.api.routes.journeys import router as journeys_router
from masar.presentation.api.routes.notes import router as notes_router
from masar.presentation.api.routes.progress import router as progress_router
from masar.presentation.api.routes.root import router as root_router
from masar.presentation.api.routes.sections import router as sections_router
from masar.presentation.api.routes.topics import router as topics_router

__all__ = [
    "root_router",
    "journeys_router",
    "sections_router",
    "topics_router",
    "notes_router",
    "progress_router",
]
