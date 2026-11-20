"""Domain exceptions package."""

from masar.domain.exceptions.ai import (
    AIAuthenticationError,
    AIConfigurationError,
    AIError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
)
from masar.domain.exceptions.base import (
    AccessDeniedError,
    DomainError,
    EmptyFieldError,
    EntityNotFoundError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)
from masar.domain.exceptions.conversation import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
    EmptyMessageError,
    InvalidMessageRoleError,
)
from masar.domain.exceptions.journey import JourneyNotFoundError
from masar.domain.exceptions.note import NoteNotFoundError
from masar.domain.exceptions.section import SectionNotFoundError
from masar.domain.exceptions.storage import (
    CorruptedStorageError,
    StorageAccessError,
    StorageError,
)
from masar.domain.exceptions.topic import TopicNotFoundError
from masar.domain.exceptions.user import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

__all__ = [
    "AIAuthenticationError",
    "AIConfigurationError",
    "AIError",
    "AIProviderError",
    "AIRateLimitError",
    "AITimeoutError",
    "AccessDeniedError",
    "AuthenticationError",
    "ConversationAccessDeniedError",
    "ConversationNotFoundError",
    "CorruptedStorageError",
    "DomainError",
    "EmptyFieldError",
    "EmptyMessageError",
    "EntityNotFoundError",
    "FieldLengthError",
    "InvalidCredentialsError",
    "InvalidIdError",
    "InvalidMessageRoleError",
    "InvalidTokenError",
    "JourneyNotFoundError",
    "NoteNotFoundError",
    "SectionNotFoundError",
    "StorageAccessError",
    "StorageError",
    "TopicNotFoundError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "ValidationError",
]
