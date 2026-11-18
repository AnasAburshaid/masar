"""Tests for Python typing compliance and type annotations."""

import ast
from pathlib import Path
import unittest

from masar.domain.types import (
    EntityId,
    JourneyId,
    NoteId,
    SectionId,
    SerializedData,
    Timestamp,
    TopicId,
)


class TestTypingAndAnnotations(unittest.TestCase):
    """Test suite ensuring complete type hint annotations and PEP 561 compliance."""

    def setUp(self) -> None:
        self.package_root = Path(__file__).resolve().parent.parent / "masar"

    def test_py_typed_marker_file_exists(self) -> None:
        """Verify PEP 561 py.typed marker file is present."""
        py_typed = self.package_root / "py.typed"
        self.assertTrue(py_typed.exists(), "masar/py.typed marker file must exist for PEP 561")

    def test_domain_type_aliases_usable(self) -> None:
        """Verify type aliases are defined and usable."""
        self.assertEqual(EntityId, int)
        self.assertEqual(JourneyId, int)
        self.assertEqual(SectionId, int)
        self.assertEqual(TopicId, int)
        self.assertEqual(NoteId, int)
        self.assertIsNotNone(Timestamp)
        self.assertIsNotNone(SerializedData)

    def test_all_public_methods_have_return_annotations(self) -> None:
        """AST check ensuring every public function and method has a return type annotation."""
        unannotated: list[str] = []

        for py_file in self.package_root.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check public functions/methods
                    if not node.name.startswith("_") and node.returns is None:
                        rel_path = py_file.relative_to(self.package_root.parent)
                        unannotated.append(f"{rel_path}:{node.lineno} {node.name}()")

        self.assertEqual(
            unannotated,
            [],
            f"Found public functions/methods without return type annotations: {unannotated}",
        )


if __name__ == "__main__":
    unittest.main()
