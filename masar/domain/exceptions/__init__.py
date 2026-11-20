"""Domain exceptions package."""

from masar.domain.exceptions.action import (
    ActionError,
    ActionExecutionError,
    ActionProposalAccessDeniedError,
    ActionProposalAlreadyResolvedError,
    ActionProposalNotFoundError,
    InvalidActionParametersError,
    UnknownToolError,
)
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
from masar.domain.exceptions.document import (
    DocumentAccessDeniedError,
    DocumentError,
    DocumentExtractionError,
    DocumentNotFoundError,
    EmptyDocumentError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from masar.domain.exceptions.journey import JourneyNotFoundError
from masar.domain.exceptions.note import NoteNotFoundError
from masar.domain.exceptions.profile import (
    ProfileAccessDeniedError,
    ProfileError,
    ProfileItemNotFoundError,
)
from masar.domain.exceptions.recommendation import RecommendationError
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
    "ActionError",
    "ActionExecutionError",
    "ActionProposalAccessDeniedError",
    "ActionProposalAlreadyResolvedError",
    "ActionProposalNotFoundError",
    "AuthenticationError",
    "ConversationAccessDeniedError",
    "ConversationNotFoundError",
    "CorruptedStorageError",
    "DocumentAccessDeniedError",
    "DocumentError",
    "DocumentExtractionError",
    "DocumentNotFoundError",
    "DomainError",
    "EmptyDocumentError",
    "EmptyFieldError",
    "EmptyMessageError",
    "EntityNotFoundError",
    "FieldLengthError",
    "FileTooLargeError",
    "InvalidActionParametersError",
    "InvalidCredentialsError",
    "InvalidIdError",
    "InvalidMessageRoleError",
    "InvalidTokenError",
    "JourneyNotFoundError",
    "NoteNotFoundError",
    "ProfileAccessDeniedError",
    "ProfileError",
    "ProfileItemNotFoundError",
    "RecommendationError",
    "SectionNotFoundError",
    "StorageAccessError",
    "StorageError",
    "TopicNotFoundError",
    "UnknownToolError",
    "UnsupportedFileTypeError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "ValidationError",
]
