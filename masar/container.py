"""Composition root and dependency injection setup for Masar."""

from masar.application.services import JourneyService, SectionService, TopicService
from masar.infrastructure.repositories.in_memory import (
    InMemoryJourneyRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)
from masar.presentation.cli import CLI


def build_container() -> tuple[JourneyService, SectionService, TopicService]:
    """Instantiate and wire up concrete repositories and application services."""
    journey_repo = InMemoryJourneyRepository()
    section_repo = InMemorySectionRepository()
    topic_repo = InMemoryTopicRepository()

    journey_service = JourneyService(
        repository=journey_repo,
        section_repository=section_repo,
        topic_repository=topic_repo,
    )
    section_service = SectionService(
        section_repository=section_repo,
        journey_repository=journey_repo,
        topic_repository=topic_repo,
    )
    topic_service = TopicService(
        topic_repository=topic_repo,
        section_repository=section_repo,
    )
    return journey_service, section_service, topic_service


def build_cli() -> CLI:
    """Build and configure the CLI presentation with wired application services."""
    journey_service, section_service, topic_service = build_container()
    return CLI(
        journey_service=journey_service,
        section_service=section_service,
        topic_service=topic_service,
    )
