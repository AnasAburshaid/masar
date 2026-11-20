"""Unit tests for ToolRegistry and ActionService."""

import json
import unittest

from masar.application.interfaces.repositories.action_proposal_repository import (
    ActionProposalRepository,
)
from masar.application.services.action_service import ActionService
from masar.application.services.ai_service import AIService
from masar.application.services.conversation_service import ConversationService
from masar.application.services.journey_service import JourneyService
from masar.application.services.note_service import NoteService
from masar.application.services.progress_service import ProgressService
from masar.application.services.section_service import SectionService
from masar.application.services.tool_registry import ServicesBundle, ToolRegistry
from masar.application.services.topic_service import TopicService
from masar.domain.exceptions.action import (
    ActionProposalAccessDeniedError,
    ActionProposalAlreadyResolvedError,
    ActionProposalNotFoundError,
    InvalidActionParametersError,
    UnknownToolError,
)
from masar.domain.models.action import ActionProposal, ProposedAction
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.repositories.in_memory import (
    InMemoryActionProposalRepository,
    InMemoryConversationRepository,
    InMemoryJourneyRepository,
    InMemoryNoteRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)


class TestActionServiceAndRegistry(unittest.TestCase):
    """Test suite for AI tool registry, proposal management, and execution."""

    def setUp(self) -> None:
        self.journey_repo = InMemoryJourneyRepository()
        self.section_repo = InMemorySectionRepository()
        self.topic_repo = InMemoryTopicRepository()
        self.note_repo = InMemoryNoteRepository()
        self.proposal_repo = InMemoryActionProposalRepository()
        self.conversation_repo = InMemoryConversationRepository()

        self.journey_service = JourneyService(
            repository=self.journey_repo,
            section_repository=self.section_repo,
            topic_repository=self.topic_repo,
            note_repository=self.note_repo,
        )
        self.section_service = SectionService(
            section_repository=self.section_repo,
            journey_repository=self.journey_repo,
            topic_repository=self.topic_repo,
            note_repository=self.note_repo,
        )
        self.topic_service = TopicService(
            topic_repository=self.topic_repo,
            section_repository=self.section_repo,
            note_repository=self.note_repo,
            journey_repository=self.journey_repo,
        )
        self.note_service = NoteService(
            note_repository=self.note_repo,
            topic_repository=self.topic_repo,
            section_repository=self.section_repo,
            journey_repository=self.journey_repo,
        )
        self.progress_service = ProgressService(
            journey_repository=self.journey_repo,
            section_repository=self.section_repo,
            topic_repository=self.topic_repo,
        )

        self.services = ServicesBundle(
            journey_service=self.journey_service,
            section_service=self.section_service,
            topic_service=self.topic_service,
            note_service=self.note_service,
            progress_service=self.progress_service,
        )

        self.registry = ToolRegistry()
        self.action_service = ActionService(
            proposal_repository=self.proposal_repo,
            tool_registry=self.registry,
            services_bundle=self.services,
        )

    def test_registry_catalog_contains_expected_tools(self) -> None:
        tools = self.registry.list_tools()
        names = {t.name for t in tools}
        expected = {
            "create_journey",
            "list_journeys",
            "get_journey",
            "update_journey",
            "delete_journey",
            "create_section",
            "list_sections",
            "update_section",
            "delete_section",
            "create_topic",
            "list_topics",
            "update_topic",
            "complete_topic",
            "pending_topic",
            "delete_topic",
            "create_note",
            "list_notes",
            "update_note",
            "delete_note",
            "get_journey_progress",
            "get_section_progress",
        }
        self.assertTrue(expected.issubset(names))

    def test_registry_unknown_tool_raises_error(self) -> None:
        with self.assertRaises(UnknownToolError):
            self.registry.get_tool("nonexistent_tool")

        with self.assertRaises(UnknownToolError):
            self.registry.execute("unknown_tool", {}, user_id=1, services=self.services)

    def test_registry_missing_required_parameters_raises_error(self) -> None:
        with self.assertRaises(InvalidActionParametersError):
            self.registry.validate_action("create_journey", {})

    def test_create_proposal_and_detect_destructive_action(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Go Fundamentals"},
            ),
            ProposedAction(
                tool="delete_journey",
                parameters={"journey_id": 99},
            ),
        ]
        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="Setup and Cleanup",
            actions=actions,
        )
        self.assertEqual(proposal.status, "pending")
        self.assertEqual(len(proposal.actions), 2)
        self.assertFalse(proposal.actions[0].is_destructive)
        self.assertTrue(proposal.actions[1].is_destructive)
        self.assertTrue(proposal.has_destructive_actions)

    def test_approve_and_execute_multi_step_with_reference_resolution(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Distributed Systems", "description": "Microservices"},
            ),
            ProposedAction(
                tool="create_section",
                parameters={"journey_id": "$0.id", "title": "Raft Consensus"},
            ),
            ProposedAction(
                tool="create_topic",
                parameters={"section_id": "$1.id", "title": "Leader Election"},
            ),
            ProposedAction(
                tool="create_note",
                parameters={"topic_id": "$prev.id", "content": "Raft paper notes"},
            ),
            ProposedAction(
                tool="complete_topic",
                parameters={"topic_id": "$2.id"},
            ),
            ProposedAction(
                tool="get_journey_progress",
                parameters={"journey_id": "$0.id"},
            ),
        ]

        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="Distributed Systems Roadmap",
            actions=actions,
        )

        executed_proposal, results = self.action_service.approve_and_execute_proposal(
            proposal_id=proposal.id or 1,
            user_id=1,
        )

        self.assertEqual(executed_proposal.status, "executed")
        self.assertEqual(len(results), 6)
        for r in results:
            self.assertEqual(r.status, "success")

        # Verify real entities created in backend services
        journeys = self.journey_service.list_journeys(user_id=1)
        self.assertEqual(len(journeys), 1)
        self.assertEqual(journeys[0].title, "Distributed Systems")

        sections = self.section_service.list_sections(journey_id=journeys[0].id or 1, user_id=1)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].title, "Raft Consensus")

        topics = self.topic_service.list_topics(section_id=sections[0].id or 1, user_id=1)
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0].title, "Leader Election")
        self.assertTrue(topics[0].is_completed)

        notes = self.note_service.list_notes(topic_id=topics[0].id or 1, user_id=1)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].content, "Raft paper notes")

        progress = self.progress_service.calculate_journey_progress(
            journey_id=journeys[0].id or 1, user_id=1
        )
        self.assertEqual(progress.completed_topics, 1)
        self.assertEqual(progress.total_topics, 1)
        self.assertEqual(progress.percentage, 100.0)

    def test_execution_failure_halts_and_marks_failed(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Valid Journey"},
            ),
            ProposedAction(
                tool="create_section",
                # Journey 99999 does not exist, triggering JourneyNotFoundError
                parameters={"journey_id": 99999, "title": "Orphan Section"},
            ),
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Never Reached Journey"},
            ),
        ]

        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="Failing Sequence",
            actions=actions,
        )

        updated_proposal, results = self.action_service.approve_and_execute_proposal(
            proposal_id=proposal.id or 1,
            user_id=1,
        )

        self.assertEqual(updated_proposal.status, "failed")
        self.assertEqual(len(results), 2)  # Stopped at step 1
        self.assertEqual(results[0].status, "success")
        self.assertEqual(results[1].status, "failure")
        self.assertIn("not found", str(results[1].error).lower())

        # Third action was never executed
        journeys = self.journey_service.list_journeys(user_id=1)
        self.assertEqual(len(journeys), 1)
        self.assertEqual(journeys[0].title, "Valid Journey")

    def test_already_resolved_proposal_cannot_be_re_approved(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "One-time Journey"},
            )
        ]
        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="Single Proposal",
            actions=actions,
        )
        self.action_service.approve_and_execute_proposal(
            proposal_id=proposal.id or 1,
            user_id=1,
        )

        with self.assertRaises(ActionProposalAlreadyResolvedError):
            self.action_service.approve_and_execute_proposal(
                proposal_id=proposal.id or 1,
                user_id=1,
            )

    def test_reject_proposal(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Rejected Roadmap"},
            )
        ]
        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="To Reject",
            actions=actions,
        )
        rejected = self.action_service.reject_proposal(
            proposal_id=proposal.id or 1,
            user_id=1,
        )
        self.assertEqual(rejected.status, "rejected")
        self.assertIsNotNone(rejected.resolved_at)

        with self.assertRaises(ActionProposalAlreadyResolvedError):
            self.action_service.approve_and_execute_proposal(
                proposal_id=proposal.id or 1,
                user_id=1,
            )

    def test_user_ownership_enforcement(self) -> None:
        actions = [
            ProposedAction(
                tool="create_journey",
                parameters={"title": "Private Journey"},
            )
        ]
        proposal = self.action_service.create_proposal(
            conversation_id=1,
            user_id=1,
            title="User 1 Plan",
            actions=actions,
        )

        # User 2 cannot access or execute User 1's proposal
        with self.assertRaises(ActionProposalAccessDeniedError):
            self.action_service.get_proposal(proposal.id or 1, user_id=2)

        with self.assertRaises(ActionProposalAccessDeniedError):
            self.action_service.approve_and_execute_proposal(proposal.id or 1, user_id=2)

        with self.assertRaises(ActionProposalAccessDeniedError):
            self.action_service.reject_proposal(proposal.id or 1, user_id=2)

    def test_conversation_service_extracts_and_creates_action_proposal(self) -> None:
        mock_ai = MockAIProvider()
        ai_service = AIService(ai_provider=mock_ai)
        conv_service = ConversationService(
            conversation_repository=self.conversation_repo,
            ai_service=ai_service,
            action_service=self.action_service,
        )

        conv = conv_service.create_conversation(user_id=1, title="Roadmap Builder")

        proposal_json = json.dumps(
            {
                "action_proposal": {
                    "title": "Build Web Dev Roadmap",
                    "actions": [
                        {
                            "tool": "create_journey",
                            "description": "Create Web Development roadmap",
                            "parameters": {"title": "Web Development", "description": "Full-stack path"},
                        },
                        {
                            "tool": "create_section",
                            "description": "Add Frontend section",
                            "parameters": {"journey_id": "$0.id", "title": "Frontend Essentials"},
                        },
                    ],
                }
            }
        )

        mock_ai.enqueue_response(
            f"I have prepared an end-to-end roadmap for you:\n\n```json\n{proposal_json}\n```\n\nPlease approve it."
        )

        user_msg, assistant_msg, proposal = conv_service.send_message(
            conversation_id=conv.id or 1,
            user_id=1,
            content="Can you build me a Web Development roadmap?",
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.title, "Build Web Dev Roadmap")
        self.assertEqual(len(proposal.actions), 2)
        self.assertEqual(proposal.status, "pending")
        # Ensure json block was stripped from assistant message text
        self.assertNotIn("```json", assistant_msg.content)
        self.assertIn("I have prepared an end-to-end roadmap", assistant_msg.content)


if __name__ == "__main__":
    unittest.main()
