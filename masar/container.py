"""Composition root and dependency injection setup for Masar."""

from pathlib import Path

from masar.application.interfaces.ai import AIProvider
from masar.application.interfaces.repositories import (
    ActionProposalRepository,
    ConversationRepository,
    JourneyRepository,
    NoteRepository,
    SectionRepository,
    TopicRepository,
    UserRepository,
)
from masar.application.services import (
    ActionService,
    AIService,
    ConversationService,
    JourneyService,
    NoteService,
    ProgressService,
    SectionService,
    ServicesBundle,
    ToolRegistry,
    TopicService,
    UserService,
)
from masar.config.settings import Settings, get_settings
from masar.infrastructure.ai import MockAIProvider, OpenRouterProvider
from masar.infrastructure.repositories.in_memory import (
    InMemoryJourneyRepository,
    InMemoryNoteRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)
from masar.infrastructure.repositories.json import (
    JsonJourneyRepository,
    JsonNoteRepository,
    JsonSectionRepository,
    JsonTopicRepository,
)
from masar.infrastructure.storage.json_storage import JsonStorage
from masar.presentation.cli import CLI


def build_container(
    storage_type: str | None = None,
    data_file: str | Path | None = None,
    database_url: str | None = None,
    settings: Settings | None = None,
) -> tuple[
    JourneyService, SectionService, TopicService, NoteService, ProgressService
]:
    """Instantiate and wire up concrete repositories and application services."""
    active_settings = settings or get_settings()
    resolved_storage = storage_type if storage_type is not None else active_settings.storage_type
    resolved_data_file = data_file if data_file is not None else active_settings.data_file

    journey_repo: JourneyRepository
    section_repo: SectionRepository
    topic_repo: TopicRepository
    note_repo: NoteRepository

    if resolved_storage == "json":
        storage = JsonStorage(resolved_data_file)
        journey_repo = JsonJourneyRepository(storage)
        section_repo = JsonSectionRepository(storage)
        topic_repo = JsonTopicRepository(storage)
        note_repo = JsonNoteRepository(storage)
    elif resolved_storage == "in_memory":
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()
    elif resolved_storage in ("database", "postgres"):
        from masar.infrastructure.database.session import Base, get_engine, get_session_factory
        from masar.infrastructure.repositories.database import (
            SqlJourneyRepository,
            SqlNoteRepository,
            SqlSectionRepository,
            SqlTopicRepository,
        )

        resolved_db_url = database_url if database_url is not None else active_settings.database_url
        engine = get_engine(resolved_db_url)
        Base.metadata.create_all(bind=engine)
        session_factory = get_session_factory(resolved_db_url)
        db_session = session_factory()
        journey_repo = SqlJourneyRepository(db_session)
        section_repo = SqlSectionRepository(db_session)
        topic_repo = SqlTopicRepository(db_session)
        note_repo = SqlNoteRepository(db_session)
    else:
        raise ValueError(f"Unknown storage type: {resolved_storage}")

    journey_service = JourneyService(
        repository=journey_repo,
        section_repository=section_repo,
        topic_repository=topic_repo,
        note_repository=note_repo,
    )
    section_service = SectionService(
        section_repository=section_repo,
        journey_repository=journey_repo,
        topic_repository=topic_repo,
        note_repository=note_repo,
    )
    topic_service = TopicService(
        topic_repository=topic_repo,
        section_repository=section_repo,
        note_repository=note_repo,
        journey_repository=journey_repo,
    )
    note_service = NoteService(
        note_repository=note_repo,
        topic_repository=topic_repo,
        section_repository=section_repo,
        journey_repository=journey_repo,
    )
    progress_service = ProgressService(
        journey_repository=journey_repo,
        section_repository=section_repo,
        topic_repository=topic_repo,
    )
    return (
        journey_service,
        section_service,
        topic_service,
        note_service,
        progress_service,
    )


def build_cli(
    storage_type: str | None = None,
    data_file: str | Path | None = None,
    database_url: str | None = None,
    settings: Settings | None = None,
) -> CLI:
    """Build and configure the CLI presentation with wired application services."""
    (
        journey_service,
        section_service,
        topic_service,
        note_service,
        progress_service,
    ) = build_container(
        storage_type=storage_type,
        data_file=data_file,
        database_url=database_url,
        settings=settings,
    )
    return CLI(
        journey_service=journey_service,
        section_service=section_service,
        topic_service=topic_service,
        note_service=note_service,
        progress_service=progress_service,
    )


def build_user_service(
    storage_type: str | None = None,
    database_url: str | None = None,
    settings: Settings | None = None,
) -> UserService:
    """Instantiate and wire up UserRepository and UserService."""
    active_settings = settings or get_settings()
    resolved_storage = storage_type if storage_type is not None else active_settings.storage_type

    user_repo: UserRepository

    if resolved_storage in ("database", "postgres"):
        from masar.infrastructure.database.session import Base, get_engine, get_session_factory
        from masar.infrastructure.repositories.database.user_repository import SqlUserRepository

        resolved_db_url = database_url if database_url is not None else active_settings.database_url
        engine = get_engine(resolved_db_url)
        Base.metadata.create_all(bind=engine)
        session_factory = get_session_factory(resolved_db_url)
        db_session = session_factory()
        user_repo = SqlUserRepository(db_session)
    elif resolved_storage in ("in_memory", "json"):
        from masar.infrastructure.repositories.in_memory.user_repository import InMemoryUserRepository

        user_repo = InMemoryUserRepository()
    else:
        raise ValueError(f"Unknown storage type: {resolved_storage}")

    from masar.infrastructure.security.jwt_token import JwtTokenService
    from masar.infrastructure.security.password import Pbkdf2PasswordHasher

    hasher = Pbkdf2PasswordHasher()
    token_service = JwtTokenService(
        secret_key=active_settings.jwt_secret_key,
        algorithm=active_settings.jwt_algorithm,
        expire_minutes=active_settings.jwt_expire_minutes,
    )
    return UserService(
        user_repository=user_repo,
        password_hasher=hasher,
        token_service=token_service,
    )


def build_ai_service(
    provider_type: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    timeout_seconds: float | None = None,
    settings: Settings | None = None,
    provider: AIProvider | None = None,
) -> AIService:
    """Instantiate and wire up AIProvider and AIService."""
    if provider is not None:
        return AIService(provider=provider)

    active_settings = settings or get_settings()
    resolved_provider = (
        provider_type if provider_type is not None else active_settings.ai_provider
    ).lower()

    resolved_model = model if model is not None else active_settings.ai_model
    resolved_timeout = (
        timeout_seconds if timeout_seconds is not None else active_settings.ai_timeout_seconds
    )

    ai_provider: AIProvider
    if resolved_provider == "openrouter":
        resolved_key = api_key if api_key is not None else active_settings.ai_api_key
        resolved_base_url = (
            base_url if base_url is not None else active_settings.ai_base_url
        )
        ai_provider = OpenRouterProvider(
            api_key=resolved_key,
            base_url=resolved_base_url,
            default_model=resolved_model,
            timeout_seconds=resolved_timeout,
            default_temperature=active_settings.ai_temperature,
            default_max_tokens=active_settings.ai_max_tokens,
        )
    elif resolved_provider == "mock":
        ai_provider = MockAIProvider(default_model=resolved_model)
    else:
        raise ValueError(f"Unknown AI provider: {resolved_provider}")

    return AIService(ai_provider=ai_provider)


def build_action_service(
    storage_type: str | None = None,
    database_url: str | None = None,
    settings: Settings | None = None,
    services_bundle: ServicesBundle | None = None,
    action_proposal_repository: ActionProposalRepository | None = None,
    tool_registry: ToolRegistry | None = None,
) -> ActionService:
    """Instantiate and wire up ActionProposalRepository, ToolRegistry, and ActionService."""
    active_settings = settings or get_settings()

    resolved_bundle: ServicesBundle
    if services_bundle is not None:
        resolved_bundle = services_bundle
    else:
        services = build_container(
            storage_type=storage_type,
            database_url=database_url,
            settings=active_settings,
        )
        resolved_bundle = ServicesBundle(
            journey_service=services[0],
            section_service=services[1],
            topic_service=services[2],
            note_service=services[3],
            progress_service=services[4],
        )

    resolved_registry = tool_registry or ToolRegistry()

    if action_proposal_repository is not None:
        return ActionService(
            proposal_repository=action_proposal_repository,
            tool_registry=resolved_registry,
            services_bundle=resolved_bundle,
        )

    resolved_storage = (
        storage_type if storage_type is not None else active_settings.storage_type
    )

    proposal_repo: ActionProposalRepository
    if resolved_storage in ("database", "postgres"):
        from masar.infrastructure.database.session import Base, get_engine, get_session_factory
        from masar.infrastructure.repositories.database.action_proposal_repository import (
            SqlActionProposalRepository,
        )

        resolved_db_url = (
            database_url if database_url is not None else active_settings.database_url
        )
        engine = get_engine(resolved_db_url)
        Base.metadata.create_all(bind=engine)
        session_factory = get_session_factory(resolved_db_url)
        db_session = session_factory()
        proposal_repo = SqlActionProposalRepository(db_session)
    elif resolved_storage in ("in_memory", "json"):
        from masar.infrastructure.repositories.in_memory.action_proposal_repository import (
            InMemoryActionProposalRepository,
        )

        proposal_repo = InMemoryActionProposalRepository()
    else:
        raise ValueError(f"Unknown storage type: {resolved_storage}")

    return ActionService(
        proposal_repository=proposal_repo,
        tool_registry=resolved_registry,
        services_bundle=resolved_bundle,
    )


def build_conversation_service(
    storage_type: str | None = None,
    database_url: str | None = None,
    settings: Settings | None = None,
    ai_service: AIService | None = None,
    conversation_repository: ConversationRepository | None = None,
    action_service: ActionService | None = None,
) -> ConversationService:
    """Instantiate and wire up ConversationRepository, AIService, ActionService, and ConversationService."""
    active_settings = settings or get_settings()
    resolved_ai = ai_service or build_ai_service(settings=active_settings)
    resolved_action_service = action_service or build_action_service(
        storage_type=storage_type,
        database_url=database_url,
        settings=active_settings,
    )

    if conversation_repository is not None:
        return ConversationService(
            conversation_repository=conversation_repository,
            ai_service=resolved_ai,
            action_service=resolved_action_service,
        )

    resolved_storage = (
        storage_type if storage_type is not None else active_settings.storage_type
    )

    conv_repo: ConversationRepository
    if resolved_storage in ("database", "postgres"):
        from masar.infrastructure.database.session import Base, get_engine, get_session_factory
        from masar.infrastructure.repositories.database.conversation_repository import (
            SqlConversationRepository,
        )

        resolved_db_url = (
            database_url if database_url is not None else active_settings.database_url
        )
        engine = get_engine(resolved_db_url)
        Base.metadata.create_all(bind=engine)
        session_factory = get_session_factory(resolved_db_url)
        db_session = session_factory()
        conv_repo = SqlConversationRepository(db_session)
    elif resolved_storage in ("in_memory", "json"):
        from masar.infrastructure.repositories.in_memory.conversation_repository import (
            InMemoryConversationRepository,
        )

        conv_repo = InMemoryConversationRepository()
    else:
        raise ValueError(f"Unknown storage type: {resolved_storage}")

    return ConversationService(
        conversation_repository=conv_repo,
        ai_service=resolved_ai,
        action_service=resolved_action_service,
    )


