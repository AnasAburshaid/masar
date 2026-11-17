"""Tests for Masar presentation layer and CLI entry point."""

import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from masar.presentation.cli import main


class TestCLI(unittest.TestCase):
    """Test CLI presentation functions and module execution."""

    def test_main_welcome_message(self) -> None:
        """Verify main() prints the welcome message and exits with status 0."""
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main()
            output = fake_stdout.getvalue()

            self.assertEqual(exit_code, 0)
            self.assertIn("Welcome to Masar - Developer Learning Tracker!", output)

    def test_module_execution(self) -> None:
        """Verify the application can be run directly using 'python -m masar'."""
        result = subprocess.run(
            [sys.executable, "-m", "masar"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Welcome to Masar - Developer Learning Tracker!", result.stdout)


if __name__ == "__main__":
    unittest.main()
