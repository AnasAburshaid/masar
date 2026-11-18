"""Architectural tests to verify layer isolation and dependency directions."""

import ast
from pathlib import Path
import unittest


class TestArchitectureAndDependencyDirection(unittest.TestCase):
    """Enforce Clean Architecture boundaries and dependency rules."""

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent / "masar"

    def _get_imports(self, file_path: Path) -> list[str]:
        """Extract imported module names from a Python source file using AST."""
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports

    def test_domain_layer_has_no_outward_dependencies(self) -> None:
        """Domain must not depend on Application, Infrastructure, or Presentation."""
        domain_dir = self.root / "domain"
        for py_file in domain_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertFalse(
                    imp.startswith("masar.application"),
                    f"Domain file {py_file.name} illegal import: {imp}",
                )
                self.assertFalse(
                    imp.startswith("masar.infrastructure"),
                    f"Domain file {py_file.name} illegal import: {imp}",
                )
                self.assertFalse(
                    imp.startswith("masar.presentation"),
                    f"Domain file {py_file.name} illegal import: {imp}",
                )

    def test_application_layer_does_not_import_infrastructure(self) -> None:
        """Application must depend on Domain and abstractions, never concrete Infrastructure."""
        app_dir = self.root / "application"
        for py_file in app_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertFalse(
                    imp.startswith("masar.infrastructure"),
                    f"Application file {py_file.name} illegally imports Infrastructure: {imp}",
                )
                self.assertFalse(
                    imp.startswith("masar.presentation"),
                    f"Application file {py_file.name} illegally imports Presentation: {imp}",
                )

    def test_presentation_does_not_import_infrastructure_directly(self) -> None:
        """Presentation layer (CLI) depends on Application and Domain, not concrete Infrastructure."""
        pres_dir = self.root / "presentation"
        for py_file in pres_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertFalse(
                    imp.startswith("masar.infrastructure"),
                    f"Presentation file {py_file.name} illegally imports Infrastructure: {imp}",
                )

    def test_container_wires_all_layers(self) -> None:
        """Container acts as composition root, building working CLI without errors."""
        from masar.container import build_cli, build_container

        services = build_container()
        self.assertEqual(len(services), 5)
        cli = build_cli()
        self.assertIsNotNone(cli)

    def test_direct_modular_imports_work(self) -> None:
        """Verify each refactored individual module can be directly imported."""
        from masar.domain.models.journey import Journey
        from masar.domain.models.section import Section
        from masar.domain.models.topic import Topic
        from masar.domain.models.note import Note
        from masar.domain.models.progress import Progress
        from masar.domain.exceptions.base import DomainError, ValidationError, EntityNotFoundError
        from masar.domain.exceptions.journey import JourneyNotFoundError
        from masar.domain.exceptions.section import SectionNotFoundError
        from masar.domain.exceptions.topic import TopicNotFoundError
        from masar.domain.exceptions.note import NoteNotFoundError
        from masar.application.interfaces.repositories.journey_repository import JourneyRepository
        from masar.application.interfaces.repositories.section_repository import SectionRepository
        from masar.application.interfaces.repositories.topic_repository import TopicRepository
        from masar.application.interfaces.repositories.note_repository import NoteRepository
        from masar.application.services.journey_service import JourneyService
        from masar.application.services.section_service import SectionService
        from masar.application.services.topic_service import TopicService
        from masar.application.services.note_service import NoteService
        from masar.application.services.progress_service import ProgressService
        from masar.infrastructure.repositories.in_memory.journey_repository import InMemoryJourneyRepository
        from masar.infrastructure.repositories.in_memory.section_repository import InMemorySectionRepository
        from masar.infrastructure.repositories.in_memory.topic_repository import InMemoryTopicRepository
        from masar.infrastructure.repositories.in_memory.note_repository import InMemoryNoteRepository

        self.assertTrue(issubclass(InMemoryJourneyRepository, JourneyRepository))
        self.assertTrue(issubclass(InMemorySectionRepository, SectionRepository))
        self.assertTrue(issubclass(InMemoryTopicRepository, TopicRepository))
        self.assertTrue(issubclass(InMemoryNoteRepository, NoteRepository))
        self.assertTrue(issubclass(JourneyNotFoundError, EntityNotFoundError))
        self.assertTrue(issubclass(SectionNotFoundError, EntityNotFoundError))
        self.assertTrue(issubclass(TopicNotFoundError, EntityNotFoundError))
        self.assertTrue(issubclass(NoteNotFoundError, EntityNotFoundError))



if __name__ == "__main__":
    unittest.main()
