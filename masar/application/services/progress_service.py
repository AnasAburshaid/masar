"""Progress application service."""

from masar.application.interfaces.repositories import (
    JourneyRepository,
    SectionRepository,
    TopicRepository,
)
from masar.domain.exceptions import JourneyNotFoundError, SectionNotFoundError
from masar.domain.models import Progress


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

    def calculate_section_progress(self, section_id: int) -> Progress:
        """Calculate progress for a specific section."""
        section = self._section_repo.get_by_id(section_id)
        if section is None:
            raise SectionNotFoundError(f"Section with ID {section_id} not found.")

        topics = self._topic_repo.get_by_section_id(section_id)
        total = len(topics)
        completed = sum(1 for topic in topics if topic.is_completed)
        return Progress(completed_topics=completed, total_topics=total)

    def calculate_journey_progress(self, journey_id: int) -> Progress:
        """Calculate overall progress for a learning journey."""
        journey = self._journey_repo.get_by_id(journey_id)
        if journey is None:
            raise JourneyNotFoundError(f"Journey with ID {journey_id} not found.")

        sections = self._section_repo.get_by_journey_id(journey_id)
        total = 0
        completed = 0
        for section in sections:
            if section.id is not None:
                topics = self._topic_repo.get_by_section_id(section.id)
                total += len(topics)
                completed += sum(1 for topic in topics if topic.is_completed)

        return Progress(completed_topics=completed, total_topics=total)
