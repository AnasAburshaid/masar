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

    def test_cli_learning_progress_workflow(self) -> None:
        """Simulate interactive session testing progress calculations, breakdown, and dynamic updates."""
        journey_repo = InMemoryJourneyRepository()
        section_repo = InMemorySectionRepository()
        topic_repo = InMemoryTopicRepository()
        note_repo = InMemoryNoteRepository()

        j_service = JourneyService(journey_repo, section_repo, topic_repo, note_repo)
        s_service = SectionService(section_repo, journey_repo, topic_repo, note_repo)
        t_service = TopicService(topic_repo, section_repo, note_repo)
        n_service = NoteService(note_repo, topic_repo)

        journey = j_service.create_journey(title="Fullstack Development")
        sec1 = s_service.create_section(journey.id, "Frontend")
        sec2 = s_service.create_section(journey.id, "Backend")

        t1 = t_service.create_topic(sec1.id, "HTML & CSS")
        t2 = t_service.create_topic(sec1.id, "JavaScript")
        t3 = t_service.create_topic(sec2.id, "Python")
        t4 = t_service.create_topic(sec2.id, "Databases")

        simulated_inputs = [
            # 1. View all journeys (shows 0.0% (0/4 topics))
            "1",
            # 2. View journey details (shows overall progress and section progress)
            "2", str(journey.id),
            # 3. View learning progress menu option 9 for non-existent journey
            "9", "999",
            # 4. View learning progress menu option 9 for valid journey
            "9", str(journey.id),
            # 5. Mark topics completed: Frontend t1, t2 -> section 1 is 100%, journey is 50%
            "7", "4", str(t1.id), "0",
            "7", "4", str(t2.id), "0",
            # 6. View learning progress again (verify 50.0% (2/4 topics))
            "9", str(journey.id),
            # 7. Mark backend topic t3 completed -> 75%
            "7", "4", str(t3.id), "0",
            # 8. View learning progress again (verify 75.0% (3/4 topics))
            "9", str(journey.id),
            # 9. Mark backend topic t3 pending -> back to 50%
            "7", "5", str(t3.id), "0",
            # 10. View journey details to verify dynamic reflection in details
            "2", str(journey.id),
            # 11. Exit
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

        # Progress menu option in main menu
        self.assertIn("9. View learning progress", combined_output)

        # Non-existent journey error
        self.assertIn("Error: Journey with ID 999 was not found.", combined_output)

        # Initial progress (0/4 topics)
        self.assertIn("0.0% (0/4 topics)", combined_output)
        self.assertIn("[          ]", combined_output)

        # Progress after completing 2 topics (50%)
        self.assertIn("50.0% (2/4 topics)", combined_output)
        self.assertIn("100.0% (2/2 topics)", combined_output)

        # Progress after completing 3rd topic (75%)
        self.assertIn("75.0% (3/4 topics)", combined_output)

        # Section breakdown
        self.assertIn("Section Breakdown:", combined_output)
        self.assertIn(f"[Section {sec1.id}] Frontend", combined_output)
        self.assertIn(f"[Section {sec2.id}] Backend", combined_output)

    def test_cli_json_persistence_across_sessions(self) -> None:
        """Verify data created in one CLI session survives restart into a second session."""
        import tempfile
        from pathlib import Path
        from masar.container import build_cli

        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "session_test.json"

            # --- Session 1: Create Data ---
            session1_inputs = [
                "3", "Data Science", "Analytics Track", # Create journey 1
                "6", "2", "1", "Pandas", "0",          # Create section 1 in journey 1
                "7", "2", "1", "DataFrames", "0",      # Create topic 1 in section 1
                "7", "4", "1", "0",                    # Mark topic 1 completed
                "8", "2", "1", "Essential for data", "0", # Create note 1
                "0",                                   # Exit
            ]
            s1_out: list[str] = []
            cli1 = build_cli(storage_type="json", data_file=data_file)
            cli1.input = lambda prompt="": session1_inputs.pop(0)
            cli1.output = lambda *args: s1_out.append(" ".join(str(a) for a in args))
            self.assertEqual(cli1.run(), 0)

            # File should exist on disk
            self.assertTrue(data_file.exists())

            # --- Session 2: Read Surviving Data ---
            session2_inputs = [
                "1",     # View all journeys (should list Data Science with 100.0% progress)
                "2", "1", # View details of journey 1
                "0",     # Exit
            ]
            s2_out: list[str] = []
            cli2 = build_cli(storage_type="json", data_file=data_file)
            cli2.input = lambda prompt="": session2_inputs.pop(0)
            cli2.output = lambda *args: s2_out.append(" ".join(str(a) for a in args))
            self.assertEqual(cli2.run(), 0)

            s2_combined = "\n".join(s2_out)
            self.assertIn("[1] Data Science", s2_combined)
            self.assertIn("100.0% (1/1 topics)", s2_combined)
            self.assertIn("[Section 1] Pandas", s2_combined)
            self.assertIn("[✓] Completed - DataFrames", s2_combined)
            self.assertIn("Essential for data", s2_combined)

    def test_cli_handles_corrupt_json_file_in_main(self) -> None:
        """Verify main() reports clear error when storage file is corrupted."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            corrupt_file = Path(temp_dir) / "corrupt.json"
            corrupt_file.write_text("{malformed json", encoding="utf-8")

            with patch("sys.stderr", new=StringIO()) as fake_stderr:
                with patch("masar.container.build_cli") as mock_build:
                    from masar.domain.exceptions import StorageError
                    mock_build.side_effect = StorageError(f"Corrupted or invalid JSON data in '{corrupt_file}'")
                    exit_code = main()
                    self.assertEqual(exit_code, 1)
                    err_msg = fake_stderr.getvalue()
                    self.assertIn("Storage Error: Corrupted or invalid JSON", err_msg)

    def test_cli_submenu_eof_handling(self) -> None:
        """Verify submenus handle unexpected EOF without raising uncaught exception."""
        from masar.container import build_cli

        inputs = ["6"] # Enter sections menu, then EOF
        out: list[str] = []
        cli = build_cli(storage_type="in_memory")
        cli.input = lambda prompt="": inputs.pop(0) if inputs else (_ for _ in ()).throw(EOFError())
        cli.output = lambda *args: out.append(" ".join(str(a) for a in args))
        exit_code = cli.run()
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
