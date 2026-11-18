"""Tests for domain models and business validation rules."""

import unittest

from masar.domain.exceptions import ValidationError
from masar.domain.models import Journey


class TestJourneyDomain(unittest.TestCase):
    """Test cases for the Journey domain entity."""

    def test_create_valid_journey(self) -> None:
        journey = Journey(title="Python Mastery", description="Learn Python deeply")
        self.assertEqual(journey.title, "Python Mastery")
        self.assertEqual(journey.description, "Learn Python deeply")
        self.assertIsNone(journey.id)
        self.assertIsNotNone(journey.created_at)

    def test_create_journey_whitespace_trimmed(self) -> None:
        journey = Journey(title="  Backend Development  ", description="  REST APIs  ")
        self.assertEqual(journey.title, "Backend Development")
        self.assertEqual(journey.description, "REST APIs")

    def test_create_journey_empty_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            Journey(title="")
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_create_journey_whitespace_title_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            Journey(title="   ")
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_update_journey_valid(self) -> None:
        journey = Journey(title="Python", description="Basics")
        journey.update(title="Advanced Python", description="Concurrency and metaprogramming")
        self.assertEqual(journey.title, "Advanced Python")
        self.assertEqual(journey.description, "Concurrency and metaprogramming")

    def test_update_journey_empty_title_raises_validation_error(self) -> None:
        journey = Journey(title="Python", description="Basics")
        with self.assertRaises(ValidationError):
            journey.update(title="   ")


if __name__ == "__main__":
    unittest.main()
