"""CLI presentation layer and command-line user interface."""

import sys
from typing import Callable

from masar.application.services import (
    JourneyService,
    NoteService,
    ProgressService,
    SectionService,
    TopicService,
)
from masar.domain.exceptions import (
    JourneyNotFoundError,
    NoteNotFoundError,
    SectionNotFoundError,
    TopicNotFoundError,
    ValidationError,
)


class CLI:
    """Command-line interface handler for Masar."""

    def __init__(
        self,
        journey_service: JourneyService | None = None,
        section_service: SectionService | None = None,
        topic_service: TopicService | None = None,
        note_service: NoteService | None = None,
        progress_service: ProgressService | None = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[..., None] = print,
    ) -> None:
        if (
            journey_service is None
            or section_service is None
            or topic_service is None
            or note_service is None
        ):
            from masar.container import build_container

            default_j, default_s, default_t, default_n, default_p = build_container()
            self.journey_service = journey_service or default_j
            self.section_service = section_service or default_s
            self.topic_service = topic_service or default_t
            self.note_service = note_service or default_n
            self.progress_service = progress_service or default_p
        else:
            self.journey_service = journey_service
            self.section_service = section_service
            self.topic_service = topic_service
            self.note_service = note_service
            if progress_service is not None:
                self.progress_service = progress_service
            elif (
                hasattr(self.journey_service, "_repository")
                and hasattr(self.section_service, "_section_repository")
                and hasattr(self.topic_service, "_topic_repository")
            ):
                self.progress_service = ProgressService(
                    journey_repository=self.journey_service._repository,
                    section_repository=self.section_service._section_repository,
                    topic_repository=self.topic_service._topic_repository,
                )
            else:
                from masar.container import build_container

                _, _, _, _, default_p = build_container()
                self.progress_service = default_p

        # Backward compatibility alias
        self.service = self.journey_service
        self.input = input_func
        self.output = output_func

    def _parse_id(self, raw_input: str) -> int | None:
        """Parse numerical ID or return None if invalid."""
        try:
            return int(raw_input.strip())
        except ValueError:
            self.output("Error: Invalid ID. Please enter a numerical ID.")
            return None

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
        self.output("6. Manage sections")
        self.output("7. Manage topics")
        self.output("8. Manage notes")
        self.output("9. View learning progress")
        self.output("0. Exit")

    # --- Journey Handlers ---

    def handle_list_journeys(self) -> None:
        """List all existing journeys with progress."""
        journeys = self.journey_service.list_journeys()
        if not journeys:
            self.output("No learning journeys found. Start by creating one!")
            return

        self.output("\n--- All Learning Journeys ---")
        for journey in journeys:
            if journey.id is not None:
                progress = self.progress_service.calculate_journey_progress(journey.id)
                self.output(f"[{journey.id}] {journey.title} - Progress: {progress.formatted}")
            else:
                self.output(f"[{journey.id}] {journey.title}")

    def handle_view_journey(self) -> None:
        """Display details of a specific journey including sections, topics, notes, and progress."""
        journey_id = self._parse_id(self.input("Enter journey ID: "))
        if journey_id is None:
            return

        try:
            journey = self.journey_service.get_journey(journey_id)
            self.output("\n--- Journey Details ---")
            self.output(f"ID: {journey.id}")
            self.output(f"Title: {journey.title}")
            description = journey.description if journey.description else "(No description)"
            self.output(f"Description: {description}")
            self.output(f"Created At: {journey.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

            journey_prog = self.progress_service.calculate_journey_progress(journey.id)  # type: ignore[arg-type]
            self.output(f"Progress: {journey_prog.progress_bar()} {journey_prog.formatted}")

            sections = self.section_service.list_sections(journey.id)  # type: ignore[arg-type]
            if not sections:
                self.output("\nSections: (No sections created yet)")
            else:
                self.output("\nSections & Topics:")
                for section in sections:
                    sec_prog = self.progress_service.calculate_section_progress(section.id)  # type: ignore[arg-type]
                    self.output(f"  [Section {section.id}] {section.title} - Progress: {sec_prog.formatted}")
                    topics = self.topic_service.list_topics(section.id)  # type: ignore[arg-type]
                    if not topics:
                        self.output("    (No topics yet)")
                    else:
                        for topic in topics:
                            status_str = "[✓] Completed" if topic.is_completed else "[ ] Pending"
                            notes = self.note_service.list_notes(topic.id)  # type: ignore[arg-type]
                            notes_suffix = f" ({len(notes)} notes)" if notes else ""
                            self.output(f"    • [Topic {topic.id}] {status_str} - {topic.title}{notes_suffix}")
                            for note in notes:
                                self.output(f"      - [Note {note.id}] {note.content}")
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_create_journey(self) -> None:
        """Create a new learning journey."""
        title = self.input("Enter journey title: ")
        description = self.input("Enter journey description (optional): ")
        try:
            journey = self.journey_service.create_journey(title=title, description=description)
            self.output(f"Success: Journey '{journey.title}' created with ID {journey.id}.")
        except ValidationError as err:
            self.output(f"Error: {err}")

    def handle_update_journey(self) -> None:
        """Update an existing journey."""
        journey_id = self._parse_id(self.input("Enter journey ID to update: "))
        if journey_id is None:
            return

        try:
            self.journey_service.get_journey(journey_id)
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")
            return

        title = self.input("Enter new title: ")
        description = self.input("Enter new description (optional): ")
        try:
            updated = self.journey_service.update_journey(journey_id, title=title, description=description)
            self.output(f"Success: Journey [{updated.id}] updated successfully.")
        except ValidationError as err:
            self.output(f"Error: {err}")

    def handle_delete_journey(self) -> None:
        """Delete an existing journey."""
        journey_id = self._parse_id(self.input("Enter journey ID to delete: "))
        if journey_id is None:
            return

        try:
            self.journey_service.delete_journey(journey_id)
            self.output(f"Success: Journey [{journey_id}] deleted successfully.")
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    # --- Section Handlers ---

    def handle_sections_menu(self) -> None:
        """Submenu for managing sections."""
        while True:
            self.output("\n--- Manage Sections ---")
            self.output("1. List sections for a journey")
            self.output("2. Add section to a journey")
            self.output("3. Rename a section")
            self.output("4. Delete a section")
            self.output("0. Back to main menu")

            choice = self.input("Enter choice: ").strip()
            if choice == "1":
                self.handle_list_sections()
            elif choice == "2":
                self.handle_create_section()
            elif choice == "3":
                self.handle_rename_section()
            elif choice == "4":
                self.handle_delete_section()
            elif choice == "0":
                break
            else:
                self.output("Error: Invalid choice. Please choose a valid option.")

    def handle_list_sections(self) -> None:
        """List sections for a given journey."""
        journey_id = self._parse_id(self.input("Enter journey ID: "))
        if journey_id is None:
            return

        try:
            sections = self.section_service.list_sections(journey_id)
            if not sections:
                self.output(f"No sections found in journey [{journey_id}].")
                return

            self.output(f"\n--- Sections in Journey [{journey_id}] ---")
            for section in sections:
                if section.id is not None:
                    sec_prog = self.progress_service.calculate_section_progress(section.id)
                    self.output(f"[Section {section.id}] {section.title} - Progress: {sec_prog.formatted}")
                else:
                    self.output(f"[Section {section.id}] {section.title}")
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_create_section(self) -> None:
        """Add a section to a journey."""
        journey_id = self._parse_id(self.input("Enter journey ID: "))
        if journey_id is None:
            return

        title = self.input("Enter section title: ")
        try:
            section = self.section_service.create_section(journey_id, title)
            self.output(f"Success: Section '{section.title}' created with ID {section.id}.")
        except (JourneyNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_rename_section(self) -> None:
        """Rename an existing section."""
        section_id = self._parse_id(self.input("Enter section ID to rename: "))
        if section_id is None:
            return

        title = self.input("Enter new section title: ")
        try:
            section = self.section_service.rename_section(section_id, title)
            self.output(f"Success: Section [{section.id}] renamed to '{section.title}'.")
        except (SectionNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_delete_section(self) -> None:
        """Delete a section."""
        section_id = self._parse_id(self.input("Enter section ID to delete: "))
        if section_id is None:
            return

        try:
            self.section_service.delete_section(section_id)
            self.output(f"Success: Section [{section_id}] deleted successfully.")
        except SectionNotFoundError as err:
            self.output(f"Error: {err}")

    # --- Topic Handlers ---

    def handle_topics_menu(self) -> None:
        """Submenu for managing topics."""
        while True:
            self.output("\n--- Manage Topics ---")
            self.output("1. List topics in a section")
            self.output("2. Add topic to a section")
            self.output("3. Rename a topic")
            self.output("4. Mark topic as completed")
            self.output("5. Mark topic as pending")
            self.output("6. Delete a topic")
            self.output("0. Back to main menu")

            choice = self.input("Enter choice: ").strip()
            if choice == "1":
                self.handle_list_topics()
            elif choice == "2":
                self.handle_create_topic()
            elif choice == "3":
                self.handle_rename_topic()
            elif choice == "4":
                self.handle_set_topic_completion(True)
            elif choice == "5":
                self.handle_set_topic_completion(False)
            elif choice == "6":
                self.handle_delete_topic()
            elif choice == "0":
                break
            else:
                self.output("Error: Invalid choice. Please choose a valid option.")

    def handle_list_topics(self) -> None:
        """List topics for a given section."""
        section_id = self._parse_id(self.input("Enter section ID: "))
        if section_id is None:
            return

        try:
            topics = self.topic_service.list_topics(section_id)
            if not topics:
                self.output(f"No topics found in section [{section_id}].")
                return

            self.output(f"\n--- Topics in Section [{section_id}] ---")
            for topic in topics:
                status_str = "[✓] Completed" if topic.is_completed else "[ ] Pending"
                self.output(f"[Topic {topic.id}] {status_str} - {topic.title}")
        except SectionNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_create_topic(self) -> None:
        """Add a topic to a section."""
        section_id = self._parse_id(self.input("Enter section ID: "))
        if section_id is None:
            return

        title = self.input("Enter topic title: ")
        try:
            topic = self.topic_service.create_topic(section_id, title)
            self.output(f"Success: Topic '{topic.title}' created with ID {topic.id}.")
        except (SectionNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_rename_topic(self) -> None:
        """Rename an existing topic."""
        topic_id = self._parse_id(self.input("Enter topic ID to rename: "))
        if topic_id is None:
            return

        title = self.input("Enter new topic title: ")
        try:
            topic = self.topic_service.rename_topic(topic_id, title)
            self.output(f"Success: Topic [{topic.id}] renamed to '{topic.title}'.")
        except (TopicNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_set_topic_completion(self, completed: bool) -> None:
        """Set topic completion status."""
        action_name = "completed" if completed else "pending"
        topic_id = self._parse_id(self.input(f"Enter topic ID to mark as {action_name}: "))
        if topic_id is None:
            return

        try:
            topic = self.topic_service.set_topic_completion(topic_id, completed)
            self.output(f"Success: Topic [{topic.id}] marked as {action_name}.")
        except TopicNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_delete_topic(self) -> None:
        """Delete a topic."""
        topic_id = self._parse_id(self.input("Enter topic ID to delete: "))
        if topic_id is None:
            return

        try:
            self.topic_service.delete_topic(topic_id)
            self.output(f"Success: Topic [{topic_id}] deleted successfully.")
        except TopicNotFoundError as err:
            self.output(f"Error: {err}")

    # --- Note Handlers ---

    def handle_notes_menu(self) -> None:
        """Submenu for managing notes attached to topics."""
        while True:
            self.output("\n--- Manage Notes ---")
            self.output("1. List notes for a topic")
            self.output("2. Add note to a topic")
            self.output("3. Edit a note")
            self.output("4. Delete a note")
            self.output("0. Back to main menu")

            choice = self.input("Enter choice: ").strip()
            if choice == "1":
                self.handle_list_notes()
            elif choice == "2":
                self.handle_create_note()
            elif choice == "3":
                self.handle_edit_note()
            elif choice == "4":
                self.handle_delete_note()
            elif choice == "0":
                break
            else:
                self.output("Error: Invalid choice. Please choose a valid option.")

    def handle_list_notes(self) -> None:
        """List notes for a given topic."""
        topic_id = self._parse_id(self.input("Enter topic ID: "))
        if topic_id is None:
            return

        try:
            notes = self.note_service.list_notes(topic_id)
            if not notes:
                self.output(f"No notes found for topic [{topic_id}].")
                return

            self.output(f"\n--- Notes for Topic [{topic_id}] ---")
            for note in notes:
                self.output(f"[Note {note.id}] {note.content}")
        except TopicNotFoundError as err:
            self.output(f"Error: {err}")

    def handle_create_note(self) -> None:
        """Add a note to a topic."""
        topic_id = self._parse_id(self.input("Enter topic ID: "))
        if topic_id is None:
            return

        content = self.input("Enter note content: ")
        try:
            note = self.note_service.create_note(topic_id, content)
            self.output(f"Success: Note created with ID {note.id} for topic [{topic_id}].")
        except (TopicNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_edit_note(self) -> None:
        """Edit an existing note."""
        note_id = self._parse_id(self.input("Enter note ID to edit: "))
        if note_id is None:
            return

        content = self.input("Enter new note content: ")
        try:
            note = self.note_service.update_note(note_id, content)
            self.output(f"Success: Note [{note.id}] updated successfully.")
        except (NoteNotFoundError, ValidationError) as err:
            self.output(f"Error: {err}")

    def handle_delete_note(self) -> None:
        """Delete a note."""
        note_id = self._parse_id(self.input("Enter note ID to delete: "))
        if note_id is None:
            return

        try:
            self.note_service.delete_note(note_id)
            self.output(f"Success: Note [{note_id}] deleted successfully.")
        except NoteNotFoundError as err:
            self.output(f"Error: {err}")

    # --- Progress Handlers ---

    def handle_view_progress(self) -> None:
        """Display learning progress overview and section breakdown for a journey."""
        journey_id = self._parse_id(self.input("Enter journey ID: "))
        if journey_id is None:
            return

        try:
            journey = self.journey_service.get_journey(journey_id)
            journey_prog = self.progress_service.calculate_journey_progress(journey_id)
            self.output(f"\n--- Learning Progress for '{journey.title}' [ID: {journey.id}] ---")
            self.output(f"Overall Progress: {journey_prog.progress_bar()} {journey_prog.formatted}")

            sections = self.section_service.list_sections(journey_id)
            if not sections:
                self.output("No sections found in this journey.")
            else:
                self.output("\nSection Breakdown:")
                for section in sections:
                    if section.id is not None:
                        sec_prog = self.progress_service.calculate_section_progress(section.id)
                        self.output(
                            f"  [Section {section.id}] {section.title}: {sec_prog.progress_bar()} {sec_prog.formatted}"
                        )
        except JourneyNotFoundError as err:
            self.output(f"Error: {err}")

    # --- Main Loop ---

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
                elif choice == "6":
                    self.handle_sections_menu()
                elif choice == "7":
                    self.handle_topics_menu()
                elif choice == "8":
                    self.handle_notes_menu()
                elif choice == "9":
                    self.handle_view_progress()
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
    from masar.container import build_cli

    cli = build_cli()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
