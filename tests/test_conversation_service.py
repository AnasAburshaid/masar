"""Unit tests for ConversationService."""

import unittest

from masar.application.services.ai_service import AIService
from masar.application.services.conversation_service import ConversationService
from masar.application.services.journey_service import JourneyService
from masar.application.services.note_service import NoteService
from masar.application.services.progress_service import ProgressService
from masar.application.services.section_service import SectionService
from masar.application.services.tool_registry import ServicesBundle
from masar.application.services.topic_service import TopicService
from masar.domain.exceptions.base import EmptyFieldError, InvalidIdError
from masar.domain.exceptions.conversation import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.repositories.in_memory.conversation_repository import (
    InMemoryConversationRepository,
)
from masar.infrastructure.repositories.in_memory.journey_repository import (
    InMemoryJourneyRepository,
)
from masar.infrastructure.repositories.in_memory.note_repository import (
    InMemoryNoteRepository,
)
from masar.infrastructure.repositories.in_memory.section_repository import (
    InMemorySectionRepository,
)
from masar.infrastructure.repositories.in_memory.topic_repository import (
    InMemoryTopicRepository,
)


class TestConversationService(unittest.TestCase):
    """Test suite for ConversationService orchestration and ownership validation."""

    def setUp(self) -> None:
        self.repo = InMemoryConversationRepository()
        self.mock_ai = MockAIProvider(
            default_response="Here is a structured learning plan.",
            default_model="mock-chat-model",
        )
        self.ai_service = AIService(ai_provider=self.mock_ai)
        self.service = ConversationService(
            conversation_repository=self.repo,
            ai_service=self.ai_service,
        )

    def test_create_conversation_default_title(self) -> None:
        conv = self.service.create_conversation(user_id=1)
        self.assertEqual(conv.user_id, 1)
        self.assertEqual(conv.title, "New Conversation")
        self.assertIsNotNone(conv.id)

    def test_create_conversation_custom_title(self) -> None:
        conv = self.service.create_conversation(user_id=1, title="Python Architecture")
        self.assertEqual(conv.title, "Python Architecture")

    def test_create_conversation_invalid_user_id(self) -> None:
        with self.assertRaises(InvalidIdError):
            self.service.create_conversation(user_id=0)

    def test_list_conversations_user_isolation(self) -> None:
        self.service.create_conversation(user_id=1, title="User 1 Conv A")
        self.service.create_conversation(user_id=1, title="User 1 Conv B")
        self.service.create_conversation(user_id=2, title="User 2 Conv")

        user1_convs = self.service.list_conversations(user_id=1)
        user2_convs = self.service.list_conversations(user_id=2)

        self.assertEqual(len(user1_convs), 2)
        self.assertEqual(len(user2_convs), 1)
        self.assertEqual(user2_convs[0].title, "User 2 Conv")

    def test_get_conversation_success(self) -> None:
        created = self.service.create_conversation(user_id=1, title="FastAPI Deep Dive")
        conv, messages = self.service.get_conversation(
            conversation_id=created.id or 1, user_id=1
        )
        self.assertEqual(conv.id, created.id)
        self.assertEqual(len(messages), 0)

    def test_get_conversation_not_found(self) -> None:
        with self.assertRaises(ConversationNotFoundError):
            self.service.get_conversation(conversation_id=999, user_id=1)

    def test_get_conversation_access_denied(self) -> None:
        created = self.service.create_conversation(user_id=1, title="Private Chat")
        with self.assertRaises(ConversationAccessDeniedError):
            self.service.get_conversation(
                conversation_id=created.id or 1, user_id=2
            )

    def test_update_title_success(self) -> None:
        conv = self.service.create_conversation(user_id=1)
        updated = self.service.update_title(
            conversation_id=conv.id or 1, user_id=1, title="Renamed Thread"
        )
        self.assertEqual(updated.title, "Renamed Thread")

    def test_delete_conversation_success(self) -> None:
        conv = self.service.create_conversation(user_id=1)
        deleted = self.service.delete_conversation(
            conversation_id=conv.id or 1, user_id=1
        )
        self.assertTrue(deleted)

        with self.assertRaises(ConversationNotFoundError):
            self.service.get_conversation(conversation_id=conv.id or 1, user_id=1)

    def test_send_message_multi_turn_and_auto_title(self) -> None:
        conv = self.service.create_conversation(user_id=1)
        self.mock_ai.enqueue_response("FastAPI provides dependency injection.")

        user_msg, assistant_msg, proposal = self.service.send_message(
            conversation_id=conv.id or 1,
            user_id=1,
            content="How does FastAPI dependency injection work?",
        )
        self.assertIsNone(proposal)

        self.assertEqual(user_msg.role, "user")
        self.assertEqual(
            user_msg.content, "How does FastAPI dependency injection work?"
        )
        self.assertEqual(assistant_msg.role, "assistant")
        self.assertEqual(
            assistant_msg.content, "FastAPI provides dependency injection."
        )

        # Verify auto-generated title
        reloaded_conv, messages = self.service.get_conversation(
            conversation_id=conv.id or 1, user_id=1
        )
        self.assertIn("FastAPI dependency injection", reloaded_conv.title)
        self.assertEqual(len(messages), 2)

        # Send second message (multi-turn verification)
        self.mock_ai.enqueue_response("You use the Depends() decorator.")
        user_msg2, assistant_msg2, proposal2 = self.service.send_message(
            conversation_id=conv.id or 1,
            user_id=1,
            content="What decorator is used?",
        )
        self.assertIsNone(proposal2)

        self.assertEqual(user_msg2.content, "What decorator is used?")
        self.assertEqual(
            assistant_msg2.content, "You use the Depends() decorator."
        )

        _, all_msgs = self.service.get_conversation(
            conversation_id=conv.id or 1, user_id=1
        )
        self.assertEqual(len(all_msgs), 4)

        # Verify mock AI recorded multi-turn call
        last_call = self.mock_ai.recorded_calls[-1]
        self.assertEqual(last_call["type"], "chat")
        # System prompt + 2 prior messages + 1 new user message = 4 messages in history + 1 assistant from turn 1 = 5
        self.assertGreaterEqual(len(last_call["messages"]), 4)

    def test_send_message_empty_content_fails(self) -> None:
        conv = self.service.create_conversation(user_id=1)
        with self.assertRaises(EmptyFieldError):
            self.service.send_message(
                conversation_id=conv.id or 1, user_id=1, content="   "
            )

    def test_extract_action_proposal_cleans_content_completely(self) -> None:
        content_with_json = (
            "I have designed a comprehensive 12-week roadmap for you!\n\n"
            "### Learning Phases\n"
            "- Phase 1: Core Networking\n"
            "- Phase 2: Consensus\n\n"
            "```proposal\n"
            "{\n"
            '  "action_proposal": {\n'
            '    "title": "Distributed Systems Roadmap",\n'
            '    "actions": [\n'
            '      {\n'
            '        "tool": "create_journey",\n'
            '        "description": "Create Distributed Systems journey",\n'
            '        "parameters": {"title": "Distributed Systems", "description": "12-week deep dive"}\n'
            '      },\n'
            '      {\n'
            '        "tool": "create_section",\n'
            '        "description": "Foundations section",\n'
            '        "parameters": {"journey_id": "$0.id", "title": "Foundations"}\n'
            '      }\n'
            '    ]\n'
            '  }\n'
            "}\n"
            "```"
        )
        cleaned, proposal = self.service._extract_action_proposal(content_with_json)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["title"], "Distributed Systems Roadmap")
        self.assertEqual(len(proposal["actions"]), 2)
        # Ensure all raw JSON and fences are removed from conversational text
        self.assertNotIn("```proposal", cleaned)
        self.assertNotIn("action_proposal", cleaned)
        self.assertNotIn("create_journey", cleaned)
        self.assertIn("I have designed a comprehensive 12-week roadmap for you!", cleaned)
        self.assertIn("### Learning Phases", cleaned)

    def test_learning_planner_context_building(self) -> None:
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()

        journey_svc = JourneyService(journey_repo, section_repo, topic_repo, note_repo)
        section_svc = SectionService(section_repo, journey_repo, topic_repo, note_repo)
        topic_svc = TopicService(topic_repo, section_repo, note_repo, journey_repo)
        note_svc = NoteService(note_repo, topic_repo, section_repo, journey_repo)
        progress_svc = ProgressService(journey_repo, section_repo, topic_repo)

        bundle = ServicesBundle(
            journey_service=journey_svc,
            section_service=section_svc,
            topic_service=topic_svc,
            note_service=note_svc,
            progress_service=progress_svc,
        )

        service_with_bundle = ConversationService(
            conversation_repository=self.repo,
            ai_service=self.ai_service,
            services_bundle=bundle,
        )

        # 1. When user has no journeys
        empty_ctx = service_with_bundle._build_user_context(user_id=10)
        self.assertIn("no existing learning journeys", empty_ctx)

        # 2. Populate journeys, sections, topics
        j = journey_svc.create_journey(title="Python Systems", description="Core Python", user_id=10)
        s = section_svc.create_section(journey_id=j.id or 1, title="Advanced Concurrency", user_id=10)
        topic_svc.create_topic(section_id=s.id or 1, title="asyncio Internals", user_id=10)

        populated_ctx = service_with_bundle._build_user_context(user_id=10)
        self.assertIn("Python Systems", populated_ctx)
        self.assertIn("Advanced Concurrency", populated_ctx)
        self.assertIn("asyncio Internals", populated_ctx)
        self.assertIn(f"Journey #{j.id}", populated_ctx)
        self.assertIn(f"Section #{s.id}", populated_ctx)


if __name__ == "__main__":
    unittest.main()
