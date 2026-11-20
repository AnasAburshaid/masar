"""Progress application service."""

from masar.application.interfaces.repositories import (
    JourneyRepository,
    SectionRepository,
    TopicRepository,
)
from masar.domain.exceptions import (
    AccessDeniedError,
    JourneyNotFoundError,
    SectionNotFoundError,
)
from masar.domain.models import Journey, Progress, Section


class ProgressService:
    """Service responsible for calculating learning progress."""

    def __init__(
        self,
        journey_repository: JourneyRepository,
        section_repository: SectionRepository,
        topic_repository: TopicRepository,
    ) -> None:
        self._journey_repo = journey_repository
        self._section_repo = section_repository
        self._topic_repo = topic_repository

    def calculate_section_progress(
        self,
        section_id: int,
        user_id: int | None = None,
    ) -> Progress:
        """Calculate progress for a specific section."""
        section = self._section_repo.get_by_id(section_id)
        if section is None:
            raise SectionNotFoundError(f"Section with ID {section_id} not found.")

        if user_id is not None:
            journey = self._journey_repo.get_by_id(section.journey_id)
            if journey and journey.user_id is not None and journey.user_id != user_id:
                raise AccessDeniedError("You do not have permission to view progress for this section.")

        topics = self._topic_repo.get_by_section_id(section_id)
        total = len(topics)
        completed = sum(1 for topic in topics if topic.is_completed)
        return Progress(completed_topics=completed, total_topics=total)

    def calculate_journey_progress(
        self,
        journey_id: int,
        user_id: int | None = None,
    ) -> Progress:
        """Calculate overall progress for a learning journey."""
        journey = self._journey_repo.get_by_id(journey_id)
        if journey is None:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} not found.")

        if user_id is not None and journey.user_id is not None and journey.user_id != user_id:
            raise AccessDeniedError("You do not have permission to view progress for this journey.")

        sections = self._section_repo.get_by_journey_id(journey_id)
        total = 0
        completed = 0
        for section in sections:
            if section.id is not None:
                topics = self._topic_repo.get_by_section_id(section.id)
                total += len(topics)
                completed += sum(1 for topic in topics if topic.is_completed)

        return Progress(completed_topics=completed, total_topics=total)

    def calculate_journey_detailed_progress(
        self,
        journey_id: int,
        user_id: int | None = None,
    ) -> tuple[Journey, Progress, list[tuple[Section, Progress]]]:
        """Calculate progress for a journey along with per-section progress breakdown."""
        journey = self._journey_repo.get_by_id(journey_id)
        if journey is None:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} not found.")

        if user_id is not None and journey.user_id is not None and journey.user_id != user_id:
            raise AccessDeniedError("You do not have permission to view progress for this journey.")

        sections = self._section_repo.get_by_journey_id(journey_id)
        section_progress_list: list[tuple[Section, Progress]] = []
        total_topics = 0
        completed_topics = 0

        for section in sections:
            if section.id is not None:
                topics = self._topic_repo.get_by_section_id(section.id)
                s_total = len(topics)
                s_completed = sum(1 for topic in topics if topic.is_completed)
                progress = Progress(completed_topics=s_completed, total_topics=s_total)
                section_progress_list.append((section, progress))
                total_topics += s_total
                completed_topics += s_completed

        journey_progress = Progress(completed_topics=completed_topics, total_topics=total_topics)
        return journey, journey_progress, section_progress_list
