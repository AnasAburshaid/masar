"""Unit tests for RecommendationService."""

import unittest

from masar.application.services.ai_service import AIService
from masar.application.services.journey_service import JourneyService
from masar.application.services.note_service import NoteService
from masar.application.services.profile_service import ProfileService
from masar.application.services.progress_service import ProgressService
from masar.application.services.recommendation_service import RecommendationService
from masar.application.services.section_service import SectionService
from masar.application.services.topic_service import TopicService
from masar.domain.exceptions.base import InvalidIdError
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.repositories.in_memory.document_repository import (
    InMemoryDocumentRepository,
)
from masar.infrastructure.repositories.in_memory.journey_repository import (
    InMemoryJourneyRepository,
)
from masar.infrastructure.repositories.in_memory.note_repository import (
    InMemoryNoteRepository,
)
from masar.infrastructure.repositories.in_memory.profile_repository import (
    InMemoryProfileRepository,
)
from masar.infrastructure.repositories.in_memory.section_repository import (
    InMemorySectionRepository,
)
from masar.infrastructure.repositories.in_memory.topic_repository import (
    InMemoryTopicRepository,
)


class TestRecommendationService(unittest.TestCase):
    """Test suite for RecommendationService algorithms and AI proposals."""

    def setUp(self) -> None:
        self.journey_repo = InMemoryJourneyRepository()
        self.section_repo = InMemorySectionRepository()
        self.topic_repo = InMemoryTopicRepository()
        self.note_repo = InMemoryNoteRepository()
        self.profile_repo = InMemoryProfileRepository()
        self.doc_repo = InMemoryDocumentRepository()

        self.journey_srv = JourneyService(self.journey_repo)
        self.section_srv = SectionService(self.section_repo, self.journey_repo)
        self.topic_srv = TopicService(self.topic_repo, self.section_repo)
        self.note_srv = NoteService(self.note_repo, self.topic_repo)
        self.progress_srv = ProgressService(
            self.journey_repo, self.section_repo, self.topic_repo
        )

        self.mock_ai = MockAIProvider(
            default_response='{"improvements": [{"title": "Async IO Internals", "reason": "Deepens understanding of event loops and non-blocking sockets."}]}',
            default_model="mock-recommender",
        )
        self.ai_service = AIService(ai_provider=self.mock_ai)

        self.profile_srv = ProfileService(
            profile_repository=self.profile_repo,
            ai_service=self.ai_service,
            document_repository=self.doc_repo,
        )

        self.service = RecommendationService(
            journey_service=self.journey_srv,
            section_service=self.section_srv,
            topic_service=self.topic_srv,
            note_service=self.note_srv,
            progress_service=self.progress_srv,
            profile_service=self.profile_srv,
            ai_service=self.ai_service,
        )

    def test_empty_user_recommendations(self) -> None:
        summary = self.service.get_recommendations(user_id=1)
        self.assertEqual(summary.user_id, 1)
        self.assertEqual(summary.total_completed_topics, 0)
        self.assertEqual(summary.total_in_progress_topics, 0)
        self.assertEqual(len(summary.recommendations), 0)
        self.assertEqual(len(summary.knowledge_gaps), 0)

    def test_next_topic_recommendation(self) -> None:
        # Create journey, section, 2 topics
        j = self.journey_srv.create_journey(title="Backend Mastery", user_id=1)
        s = self.section_srv.create_section(journey_id=j.id or 1, title="FastAPI", user_id=1)
        t1 = self.topic_srv.create_topic(section_id=s.id or 1, title="Routing", user_id=1)
        t2 = self.topic_srv.create_topic(section_id=s.id or 1, title="Dependency Injection", user_id=1)

        # Mark topic 1 complete
        self.topic_srv.set_topic_completion(topic_id=t1.id or 1, completed=True, user_id=1)

        summary = self.service.get_recommendations(user_id=1)
        self.assertEqual(summary.total_completed_topics, 1)
        self.assertEqual(summary.total_in_progress_topics, 1)

        # Should recommend topic 2
        next_topic_rec = next(
            (r for r in summary.recommendations if r.recommendation_type == "next_topic"),
            None,
        )
        self.assertIsNotNone(next_topic_rec)
        assert next_topic_rec is not None
        self.assertIn("Dependency Injection", next_topic_rec.title)
        self.assertIn("Backend Mastery", next_topic_rec.reason)
        self.assertEqual(next_topic_rec.suggested_action, "study_next")

    def test_note_difficulty_triggers_review_recommendation(self) -> None:
        j = self.journey_srv.create_journey(title="Rust Track", user_id=1)
        s = self.section_srv.create_section(journey_id=j.id or 1, title="Ownership", user_id=1)
        t = self.topic_srv.create_topic(section_id=s.id or 1, title="Borrow Checker", user_id=1)

        # Add note with difficulty keyword
        self.note_srv.create_note(
            topic_id=t.id or 1,
            content="I am very confused and stuck on lifetime annotations with mutable references.",
            user_id=1,
        )

        summary = self.service.get_recommendations(user_id=1)
        review_rec = next(
            (r for r in summary.recommendations if r.recommendation_type == "review_refresher"),
            None,
        )
        self.assertIsNotNone(review_rec)
        assert review_rec is not None
        self.assertIn("Borrow Checker", review_rec.title)
        self.assertIn("lifetime annotations", review_rec.reason)

    def test_capstone_project_recommendation_when_journey_completed(self) -> None:
        j = self.journey_srv.create_journey(title="Docker 101", user_id=1)
        s = self.section_srv.create_section(journey_id=j.id or 1, title="Containers", user_id=1)
        t = self.topic_srv.create_topic(section_id=s.id or 1, title="Images & Dockerfile", user_id=1)
        self.topic_srv.set_topic_completion(topic_id=t.id or 1, completed=True, user_id=1)

        summary = self.service.get_recommendations(user_id=1)
        capstone_rec = next(
            (r for r in summary.recommendations if "Capstone" in r.title),
            None,
        )
        self.assertIsNotNone(capstone_rec)
        assert capstone_rec is not None
        self.assertIn("Docker 101", capstone_rec.reason)

    def test_profile_goal_gap_detection(self) -> None:
        # User has an active goal "Kubernetes" in profile
        self.profile_srv.add_item(
            user_id=1,
            name="Kubernetes",
            category="goal",
            is_confirmed=True,
        )

        # User has journey for "Python", but nothing covering Kubernetes
        self.journey_srv.create_journey(title="Python Fundamentals", user_id=1)

        summary = self.service.get_recommendations(user_id=1)
        self.assertEqual(len(summary.knowledge_gaps), 1)
        gap = summary.knowledge_gaps[0]
        self.assertEqual(gap.topic_name, "Kubernetes")
        self.assertIn("goal in your profile", gap.description)

        # Check corresponding recommendation
        gap_rec = next(
            (r for r in summary.recommendations if "Kubernetes" in r.title),
            None,
        )
        self.assertIsNotNone(gap_rec)

    def test_propose_journey_improvement(self) -> None:
        j = self.journey_srv.create_journey(title="Python Concurrency", user_id=1)
        s = self.section_srv.create_section(journey_id=j.id or 1, title="Threading", user_id=1)
        self.topic_srv.create_topic(section_id=s.id or 1, title="GIL", user_id=1)

        proposals = self.service.propose_journey_improvement(
            user_id=1,
            journey_id=j.id or 1,
            feedback="I want to learn async io and high performance network servers.",
        )
        self.assertEqual(len(proposals), 1)
        prop = proposals[0]
        self.assertEqual(prop.title, "Async IO Internals")
        self.assertIn("non-blocking sockets", prop.reason)
        self.assertEqual(prop.suggested_action, "create_topic")
        self.assertEqual(prop.journey_id, j.id)

    def test_invalid_user_id_raises(self) -> None:
        with self.assertRaises(InvalidIdError):
            self.service.get_recommendations(user_id=0)


if __name__ == "__main__":
    unittest.main()
