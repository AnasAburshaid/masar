"""Application schemas package for input validation, serialization, and storage validation."""

from masar.application.schemas.action import (
    ActionApprovalResponseSchema,
    ActionProposalCreateSchema,
    ActionProposalResponseSchema,
    ActionResultSchema,
    ProposedActionSchema,
)
from masar.application.schemas.ai import (
    AIResponseSchema,
    AIUsageSchema,
    ChatMessageSchema,
    ChatRequestSchema,
    CompletionRequestSchema,
)
from masar.application.schemas.conversation import (
    ConversationCreateSchema,
    ConversationDetailResponseSchema,
    ConversationResponseSchema,
    ConversationUpdateSchema,
    MessageCreateSchema,
    MessageResponseSchema,
    SendMessageResponseSchema,
)
from masar.application.schemas.document import (
    DocumentDetailSchema,
    DocumentResponseSchema,
    DocumentSummarizeResponseSchema,
)
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
from masar.application.schemas.token import (
    LoginRequestSchema,
    TokenResponseSchema,
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
    # Action & Proposals
    "ActionApprovalResponseSchema",
    "ActionProposalCreateSchema",
    "ActionProposalResponseSchema",
    "ActionResultSchema",
    "ProposedActionSchema",
    # AI
    "AIResponseSchema",
    "AIUsageSchema",
    "ChatMessageSchema",
    "ChatRequestSchema",
    "CompletionRequestSchema",
    # Conversation
    "ConversationCreateSchema",
    "ConversationDetailResponseSchema",
    "ConversationResponseSchema",
    "ConversationUpdateSchema",
    "MessageCreateSchema",
    "MessageResponseSchema",
    "SendMessageResponseSchema",
    # Document
    "DocumentDetailSchema",
    "DocumentResponseSchema",
    "DocumentSummarizeResponseSchema",
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
    # Token
    "LoginRequestSchema",
    "TokenResponseSchema",
]
