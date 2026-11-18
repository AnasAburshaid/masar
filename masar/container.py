"""Composition root and dependency injection setup for Masar."""

from pathlib import Path

from masar.application.interfaces.repositories import (
    JourneyRepository,
    NoteRepository,
    SectionRepository,
    TopicRepository,
)
from masar.application.services import (
    JourneyService,
    NoteService,
    ProgressService,
    SectionService,
    TopicService,
)
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
    storage_type: str = "json",
    data_file: str | Path | None = None,
) -> tuple[
    JourneyService, SectionService, TopicService, NoteService, ProgressService
]:
    """Instantiate and wire up concrete repositories and application services."""
    journey_repo: JourneyRepository
    section_repo: SectionRepository
    topic_repo: TopicRepository
    note_repo: NoteRepository

    if storage_type == "json":
        storage = JsonStorage(data_file or "masar_data.json")
        journey_repo = JsonJourneyRepository(storage)
        section_repo = JsonSectionRepository(storage)
        topic_repo = JsonTopicRepository(storage)
        note_repo = JsonNoteRepository(storage)
    elif storage_type == "in_memory":
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

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
    )
    note_service = NoteService(
        note_repository=note_repo,
        topic_repository=topic_repo,
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
    storage_type: str = "json",
    data_file: str | Path | None = None,
) -> CLI:
    """Build and configure the CLI presentation with wired application services."""
    (
        journey_service,
        section_service,
        topic_service,
        note_service,
        progress_service,
    ) = build_container(storage_type=storage_type, data_file=data_file)
    return CLI(
        journey_service=journey_service,
        section_service=section_service,
        topic_service=topic_service,
        note_service=note_service,
        progress_service=progress_service,
    )
