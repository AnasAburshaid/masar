"""CLI presentation layer and command-line user interface."""

import sys
from typing import Callable

from masar.application.services import JourneyService
from masar.domain.exceptions import DomainError, JourneyNotFoundError, ValidationError


class CLI:
    """Command-line interface handler for Masar."""

    def __init__(
        self,
        service: JourneyService | None = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[..., None] = print,
    ) -> None:
        self.service = service or JourneyService()
        self.input = input_func
        self.output = output_func

    def display_welcome(self) -> None:
        """Display initial welcome greeting."""
        self.output("Welcome to Masar - Developer Learning Tracker!")

    def display_menu(self) -> None:
        """Display main navigation menu."""
        self.output("\n--- Masar Menu ---")
        self.output("1. View all journeys")
        self.output("2. View journey details")
        self.output("3. Create a journey")
        self.output("4. Update a journey")
        self.output("5. Delete a journey")
        self.output("0. Exit")

    def handle_list_journeys(self) -> None:
        """List all existing journeys."""
        journeys = self.service.list_journeys()
        if not journeys:
            self.output("No learning journeys found. Start by creating one!")
            return

        self.output("\n--- All Learning Journeys ---")
        for journey in journeys:
            self.output(f"[{journey.id}] {journey.title}")

    def handle_view_journey(self) -> None:
        """Display details of a specific journey."""
        raw_id = self.input("Enter journey ID: ").strip()
        try:
            journey_id = int(raw_id)
        except ValueError:
            self.output("Error: Invalid ID. Please enter a numerical ID.")
            return

        try:
            journey = self.service.get_journey(journey_id)
            self.output("\n--- Journey Details ---")
            self.output(f"ID: {journey.id}")
            self.output(f"Title: {journey.title}")
            description = journey.description if journey.description else "(No description)"
            self.output(f"Description: {description}")
            self.output(f"Created At: {journey.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_create_journey(self) -> None:
        """Create a new learning journey."""
        title = self.input("Enter journey title: ")
        description = self.input("Enter journey description (optional): ")
        try:
            journey = self.service.create_journey(title=title, description=description)
            self.output(f"Success: Journey '{journey.title}' created with ID {journey.id}.")
        except ValidationError as err:
            self.output(f"Error: {err}")

    def handle_update_journey(self) -> None:
        """Update an existing journey."""
        raw_id = self.input("Enter journey ID to update: ").strip()
        try:
            journey_id = int(raw_id)
        except ValueError:
            self.output("Error: Invalid ID. Please enter a numerical ID.")
            return

        try:
            # Check existence first
            self.service.get_journey(journey_id)
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")
            return

        title = self.input("Enter new title: ")
        description = self.input("Enter new description (optional): ")
        try:
            updated = self.service.update_journey(journey_id, title=title, description=description)
            self.output(f"Success: Journey [{updated.id}] updated successfully.")
        except ValidationError as err:
            self.output(f"Error: {err}")

    def handle_delete_journey(self) -> None:
        """Delete an existing journey."""
        raw_id = self.input("Enter journey ID to delete: ").strip()
        try:
            journey_id = int(raw_id)
        except ValueError:
            self.output("Error: Invalid ID. Please enter a numerical ID.")
            return

        try:
            self.service.delete_journey(journey_id)
            self.output(f"Success: Journey [{journey_id}] deleted successfully.")
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    def run(self) -> int:
        """Run the main interactive CLI loop."""
        self.display_welcome()
        while True:
            try:
                self.display_menu()
                choice = self.input("Enter your choice: ").strip()
                if choice == "1":
                    self.handle_list_journeys()
                elif choice == "2":
                    self.handle_view_journey()
                elif choice == "3":
                    self.handle_create_journey()
                elif choice == "4":
                    self.handle_update_journey()
                elif choice == "5":
                    self.handle_delete_journey()
                elif choice == "0":
                    self.output("Goodbye!")
                    break
                else:
                    self.output("Error: Invalid choice. Please choose a valid option from the menu.")
            except (EOFError, KeyboardInterrupt):
                self.output("\nGoodbye!")
                break
        return 0


def main(args: list[str] | None = None) -> int:
    """Entry point for presentation CLI."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
