"""Tests for Masar presentation layer and CLI interactive workflow."""

import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from masar.application.services import JourneyService
from masar.infrastructure.repositories import InMemoryJourneyRepository
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
        repo = InMemoryJourneyRepository()
        service = JourneyService(repo)

        # Sequence of user inputs:
        # 1. List when empty
        # 2. Create journey with invalid empty title
        # 3. Create journey with valid title and description
        # 4. List journeys (should show newly created journey)
        # 5. View details of non-existent ID (99)
        # 6. View details of invalid ID format ("abc")
        # 7. View details of valid ID (1)
        # 8. Update journey 1
        # 9. Delete journey 1
        # 10. List journeys (should be empty again)
        # 11. Invalid menu choice ("99")
        # 0. Exit
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

        cli = CLI(service=service, input_func=fake_input, output_func=fake_output)
        exit_code = cli.run()
        self.assertEqual(exit_code, 0)

        combined_output = "\n".join(output_records)

        # 1. List empty
        self.assertIn("No learning journeys found", combined_output)
        # 2. Validation error on empty title
        self.assertIn("Error: Journey title cannot be empty", combined_output)
        # 3. Creation success
        self.assertIn("Success: Journey 'Python Mastery' created with ID 1.", combined_output)
        # 4. List contains created journey
        self.assertIn("[1] Python Mastery", combined_output)
        # 5. Non-existent ID error
        self.assertIn("Error: Journey with ID 99 was not found.", combined_output)
        # 6. Invalid ID format
        self.assertIn("Error: Invalid ID. Please enter a numerical ID.", combined_output)
        # 7. Details of ID 1
        self.assertIn("Title: Python Mastery", combined_output)
        self.assertIn("Description: Learn Python 3", combined_output)
        # 8. Update success
        self.assertIn("Success: Journey [1] updated successfully.", combined_output)
        # 9. Delete success
        self.assertIn("Success: Journey [1] deleted successfully.", combined_output)
        # 10. List after delete
        self.assertIn("No learning journeys found. Start by creating one!", combined_output)
        # 11. Invalid menu choice
        self.assertIn("Error: Invalid choice. Please choose a valid option from the menu.", combined_output)
        # 12. Exit
        self.assertIn("Goodbye!", combined_output)


if __name__ == "__main__":
    unittest.main()
