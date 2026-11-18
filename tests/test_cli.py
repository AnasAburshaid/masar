"""Tests for Masar presentation layer and CLI interactive workflow."""

import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from masar.application.services import (
    JourneyService,
    NoteService,
    SectionService,
    TopicService,
)
from masar.infrastructure.repositories import (
    InMemoryJourneyRepository,
    InMemoryNoteRepository,
    InMemorySectionRepository,
    InMemoryTopicRepository,
)
from masar.presentation.cli import CLI, main


class TestCLI(unittest.TestCase):
    """Test CLI presentation functions and module execution."""

    def test_main_welcome_message(self) -> None:
        """Verify main() prints welcome message and handles non-interactive stdin gracefully."""
        with patch("sys.stdin", StringIO("0\n")), patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main()
            output = fake_stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Welcome to Masar - Developer Learning Tracker!", output)

    def test_module_execution(self) -> None:
        """Verify the application can be run directly using 'python -m masar' with clean exit."""
        result = subprocess.run(
            [sys.executable, "-m", "masar"],
            input="0\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Welcome to Masar - Developer Learning Tracker!", result.stdout)
        self.assertIn("Goodbye!", result.stdout)

    def test_cli_crud_journey_workflow(self) -> None:
        """Simulate interactive session testing all CRUD operations and error handling."""
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()
        j_service = JourneyService(journey_repo, section_repo, topic_repo, note_repo)
        s_service = SectionService(section_repo, journey_repo, topic_repo, note_repo)
        t_service = TopicService(topic_repo, section_repo, note_repo)
        n_service = NoteService(note_repo, topic_repo)

        simulated_inputs = [
            "1",                # List empty
            "3", "   ", "desc", # Create empty title
            "3", "Python Mastery", "Learn Python 3", # Create valid
            "1",                # List all
            "2", "99",          # View non-existent
            "2", "invalid_id",  # View invalid format
            "2", "1",           # View valid
            "4", "1", "Advanced Python", "Updated Description", # Update
            "5", "1",           # Delete
            "1",                # List after delete
            "99",               # Invalid choice
            "0",                # Exit
        ]

        output_records: list[str] = []

        def fake_input(prompt: str = "") -> str:
            if not simulated_inputs:
                raise EOFError()
            return simulated_inputs.pop(0)

        def fake_output(*args: object) -> None:
            output_records.append(" ".join(str(a) for a in args))

        cli = CLI(
            journey_service=j_service,
            section_service=s_service,
            topic_service=t_service,
            note_service=n_service,
            input_func=fake_input,
            output_func=fake_output,
        )
        exit_code = cli.run()
        self.assertEqual(exit_code, 0)

        combined_output = "\n".join(output_records)

        self.assertIn("No learning journeys found", combined_output)
        self.assertIn("Error: Journey title cannot be empty", combined_output)
        self.assertIn("Success: Journey 'Python Mastery' created with ID 1.", combined_output)
        self.assertIn("[1] Python Mastery", combined_output)
        self.assertIn("Error: Journey with ID 99 was not found.", combined_output)
        self.assertIn("Error: Invalid ID. Please enter a numerical ID.", combined_output)
        self.assertIn("Title: Python Mastery", combined_output)
        self.assertIn("Description: Learn Python 3", combined_output)
        self.assertIn("Success: Journey [1] updated successfully.", combined_output)
        self.assertIn("Success: Journey [1] deleted successfully.", combined_output)
        self.assertIn("No learning journeys found. Start by creating one!", combined_output)
        self.assertIn("Error: Invalid choice. Please choose a valid option from the menu.", combined_output)
        self.assertIn("Goodbye!", combined_output)

    def test_cli_sections_and_topics_workflow(self) -> None:
        """Simulate interactive session testing sections and topics workflows."""
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()
        j_service = JourneyService(journey_repo, section_repo, topic_repo, note_repo)
        s_service = SectionService(section_repo, journey_repo, topic_repo, note_repo)
        t_service = TopicService(topic_repo, section_repo, note_repo)
        n_service = NoteService(note_repo, topic_repo)

        # 1. Create a journey
        journey = j_service.create_journey(title="Python Track")

        simulated_inputs = [
            # Manage sections
            "6",
            "1", str(journey.id), # List sections (empty)
            "2", "999", "Bad Section", # Add section to non-existent journey
            "2", str(journey.id), "   ", # Add section with empty title
            "2", str(journey.id), "Python Fundamentals", # Add valid section (ID 1)
            "1", str(journey.id), # List sections (shows ID 1)
            "3", "1", "Core Python", # Rename section 1
            "0", # Back to main menu

            # Manage topics
            "7",
            "1", "1", # List topics in section 1 (empty)
            "2", "999", "Bad Topic", # Add topic to non-existent section
            "2", "1", "  ", # Add topic with empty title
            "2", "1", "Variables", # Add valid topic (ID 1)
            "2", "1", "Functions", # Add second valid topic (ID 2)
            "1", "1", # List topics in section 1
            "3", "1", "Variables and Scope", # Rename topic 1
            "4", "1", # Mark topic 1 completed
            "5", "1", # Mark topic 1 pending
            "4", "1", # Mark topic 1 completed again
            "6", "2", # Delete topic 2
            "0", # Back to main menu

            # View journey details (should display journey, section, topic with status)
            "2", str(journey.id),

            # Delete section (cascades to remaining topics)
            "6",
            "4", "1", # Delete section 1
            "0", # Back to main menu

            # Exit
            "0",
        ]

        output_records: list[str] = []

        def fake_input(prompt: str = "") -> str:
            if not simulated_inputs:
                raise EOFError()
            return simulated_inputs.pop(0)

        def fake_output(*args: object) -> None:
            output_records.append(" ".join(str(a) for a in args))

        cli = CLI(
            journey_service=j_service,
            section_service=s_service,
            topic_service=t_service,
            note_service=n_service,
            input_func=fake_input,
            output_func=fake_output,
        )
        exit_code = cli.run()
        self.assertEqual(exit_code, 0)

        combined_output = "\n".join(output_records)

        # Section verifications
        self.assertIn("No sections found in journey", combined_output)
        self.assertIn("Error: Journey with ID 999 was not found.", combined_output)
        self.assertIn("Error: Section title cannot be empty.", combined_output)
        self.assertIn("Success: Section 'Python Fundamentals' created with ID 1.", combined_output)
        self.assertIn("[Section 1] Python Fundamentals", combined_output)
        self.assertIn("Success: Section [1] renamed to 'Core Python'.", combined_output)

        # Topic verifications
        self.assertIn("No topics found in section [1].", combined_output)
        self.assertIn("Error: Section with ID 999 was not found.", combined_output)
        self.assertIn("Error: Topic title cannot be empty.", combined_output)
        self.assertIn("Success: Topic 'Variables' created with ID 1.", combined_output)
        self.assertIn("Success: Topic [1] renamed to 'Variables and Scope'.", combined_output)
        self.assertIn("Success: Topic [1] marked as completed.", combined_output)
        self.assertIn("Success: Topic [1] marked as pending.", combined_output)
        self.assertIn("Success: Topic [2] deleted successfully.", combined_output)

        # Journey details verification (includes section & topic completion status)
        self.assertIn("Sections & Topics:", combined_output)
        self.assertIn("[Section 1] Core Python", combined_output)
        self.assertIn("[Topic 1] [✓] Completed - Variables and Scope", combined_output)

        # Delete section verification
        self.assertIn("Success: Section [1] deleted successfully.", combined_output)

    def test_cli_notes_workflow(self) -> None:
        """Simulate interactive session testing notes management workflow."""
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()

        j_service = JourneyService(journey_repo, section_repo, topic_repo, note_repo)
        s_service = SectionService(section_repo, journey_repo, topic_repo, note_repo)
        t_service = TopicService(topic_repo, section_repo, note_repo)
        n_service = NoteService(note_repo, topic_repo)

        journey = j_service.create_journey(title="Python Track")
        section = s_service.create_section(journey.id, "Basics")
        topic = t_service.create_topic(section.id, "Variables")

        simulated_inputs = [
            # Manage notes menu
            "8",
            "1", str(topic.id),                 # List notes (empty)
            "2", "999", "Orphan note",          # Add note to non-existent topic
            "2", str(topic.id), "   ",          # Add note with empty content
            "2", str(topic.id), "Dynamic typing", # Add note 1
            "2", str(topic.id), "Memory model",   # Add note 2
            "1", str(topic.id),                 # List notes (should show 2 notes)
            "3", "1", "Dynamically typed variables in Python", # Edit note 1
            "3", "999", "Non-existent note",    # Edit non-existent note
            "4", "2",                           # Delete note 2
            "4", "999",                         # Delete non-existent note
            "0",                                # Back to main menu

            # View journey details (should display the topic and its remaining note)
            "2", str(journey.id),

            # Exit
            "0",
        ]

        output_records: list[str] = []

        def fake_input(prompt: str = "") -> str:
            if not simulated_inputs:
                raise EOFError()
            return simulated_inputs.pop(0)

        def fake_output(*args: object) -> None:
            output_records.append(" ".join(str(a) for a in args))

        cli = CLI(
            journey_service=j_service,
            section_service=s_service,
            topic_service=t_service,
            note_service=n_service,
            input_func=fake_input,
            output_func=fake_output,
        )
        exit_code = cli.run()
        self.assertEqual(exit_code, 0)

        combined_output = "\n".join(output_records)

        # Note validations and assertions
        self.assertIn("No notes found for topic [1].", combined_output)
        self.assertIn("Error: Topic with ID 999 was not found.", combined_output)
        self.assertIn("Error: Note content cannot be empty.", combined_output)
        self.assertIn("Success: Note created with ID 1 for topic [1].", combined_output)
        self.assertIn("Success: Note created with ID 2 for topic [1].", combined_output)
        self.assertIn("[Note 1] Dynamic typing", combined_output)
        self.assertIn("[Note 2] Memory model", combined_output)
        self.assertIn("Success: Note [1] updated successfully.", combined_output)
        self.assertIn("Error: Note with ID 999 was not found.", combined_output)
        self.assertIn("Success: Note [2] deleted successfully.", combined_output)

        # Journey details displaying note
        self.assertIn("(1 notes)", combined_output)
        self.assertIn("[Note 1] Dynamically typed variables in Python", combined_output)


if __name__ == "__main__":
    unittest.main()
