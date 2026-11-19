"""Application schemas package for input validation, serialization, and storage validation."""

from masar.application.schemas.journey import (
    JourneyCreateSchema,
    JourneyResponseSchema,
    JourneyUpdateSchema,
)
from masar.application.schemas.note import (
    NoteCreateSchema,
    NoteResponseSchema,
    NoteUpdateSchema,
)
from masar.application.schemas.progress import (
    JourneyProgressSchema,
    SectionProgressSchema,
)
from masar.application.schemas.section import (
    SectionCreateSchema,
    SectionResponseSchema,
    SectionUpdateSchema,
)
from masar.application.schemas.storage import (
    StorageDataSchema,
    StorageJourneyRecord,
    StorageNoteRecord,
    StorageSectionRecord,
    StorageTopicRecord,
    validate_storage_data,
)
from masar.application.schemas.topic import (
    TopicCreateSchema,
    TopicResponseSchema,
    TopicUpdateSchema,
)
from masar.application.schemas.user import (
    UserRegisterSchema,
    UserResponseSchema,
)

__all__ = [
    # Journey
    "JourneyCreateSchema",
    "JourneyUpdateSchema",
    "JourneyResponseSchema",
    # Section
    "SectionCreateSchema",
    "SectionUpdateSchema",
    "SectionResponseSchema",
    # Topic
    "TopicCreateSchema",
    "TopicUpdateSchema",
    "TopicResponseSchema",
    # Note
    "NoteCreateSchema",
    "NoteUpdateSchema",
    "NoteResponseSchema",
    # Progress
    "JourneyProgressSchema",
    "SectionProgressSchema",
    # Storage
    "StorageDataSchema",
    "StorageJourneyRecord",
    "StorageSectionRecord",
    "StorageTopicRecord",
    "StorageNoteRecord",
    "validate_storage_data",
    # User
    "UserRegisterSchema",
    "UserResponseSchema",
]
