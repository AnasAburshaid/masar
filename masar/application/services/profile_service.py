"""Learning profile application service managing skills, experience, and knowledge extraction."""

import json
import re
from typing import Any, Optional

from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.application.interfaces.repositories.profile_repository import (
    ProfileRepository,
)
from masar.application.services.ai_service import AIService
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.exceptions.profile import (
    ProfileAccessDeniedError,
    ProfileItemNotFoundError,
)
from masar.domain.models.ai import ChatMessage
from masar.domain.models.profile import LearningProfile, ProfileItem


class ProfileService:
    """Service handling personal learning knowledge profile management and AI extraction."""

    def __init__(
        self,
        profile_repository: ProfileRepository,
        ai_service: Optional[AIService] = None,
        document_repository: Optional[DocumentRepository] = None,
    ) -> None:
        self._repo = profile_repository
        self._ai = ai_service
        self._document_repo = document_repository

    def get_profile(self, user_id: int) -> LearningProfile:
        """Retrieve complete learning profile for a user."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        return self._repo.get_profile(user_id)

    def add_item(
        self,
        user_id: int,
        name: str,
        category: str,
        level: Optional[str] = None,
        is_confirmed: bool = True,
        source_type: str = "manual",
        source_id: Optional[int] = None,
    ) -> ProfileItem:
        """Add a new profile item."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        item = ProfileItem(
            user_id=user_id,
            name=name,
            category=category,
            level=level,
            is_confirmed=is_confirmed,
            source_type=source_type,
            source_id=source_id,
        )
        return self._repo.add_item(item)

    def confirm_item(self, user_id: int, item_id: int) -> ProfileItem:
        """Confirm an AI-inferred profile item, verifying user ownership."""
        if user_id <= 0 or item_id <= 0:
            raise InvalidIdError("User ID and Item ID must be positive integers.")

        item = self._repo.get_item(item_id)
        if item is None:
            raise ProfileItemNotFoundError(f"Profile item #{item_id} was not found.")

        if item.user_id != user_id:
            raise ProfileAccessDeniedError("Cannot confirm a profile item belonging to another user.")

        item.confirm()
        return self._repo.update_item(item)

    def update_item(
        self,
        user_id: int,
        item_id: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        is_confirmed: Optional[bool] = None,
    ) -> ProfileItem:
        """Update an existing profile item, verifying user ownership."""
        if user_id <= 0 or item_id <= 0:
            raise InvalidIdError("User ID and Item ID must be positive integers.")

        item = self._repo.get_item(item_id)
        if item is None:
            raise ProfileItemNotFoundError(f"Profile item #{item_id} was not found.")

        if item.user_id != user_id:
            raise ProfileAccessDeniedError("Cannot modify a profile item belonging to another user.")

        item.update(name=name, category=category, level=level, is_confirmed=is_confirmed)
        return self._repo.update_item(item)

    def delete_item(self, user_id: int, item_id: int) -> bool:
        """Delete a profile item, verifying user ownership."""
        if user_id <= 0 or item_id <= 0:
            raise InvalidIdError("User ID and Item ID must be positive integers.")

        item = self._repo.get_item(item_id)
        if item is None:
            raise ProfileItemNotFoundError(f"Profile item #{item_id} was not found.")

        if item.user_id != user_id:
            raise ProfileAccessDeniedError("Cannot delete a profile item belonging to another user.")

        return self._repo.delete_item(item_id)

    def update_bio(self, user_id: int, bio: str) -> None:
        """Update the user's high-level bio."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        self._repo.update_bio(user_id, bio.strip())

    def extract_from_document(self, user_id: int, document_id: int) -> list[ProfileItem]:
        """Extract skills, technologies, experience, and goals from an uploaded document.
        
        Important: Extracted items are created with is_confirmed=False so the user can review them.
        """
        if user_id <= 0 or document_id <= 0:
            raise InvalidIdError("User ID and Document ID must be positive integers.")

        if self._document_repo is None:
            raise RuntimeError("DocumentRepository is required for document profile extraction.")

        doc = self._document_repo.get_by_id(document_id)
        if doc is None or doc.user_id != user_id:
            raise ProfileAccessDeniedError("Document not found or access denied.")

        if self._ai is None:
            raise RuntimeError("AIService is required for profile extraction.")

        prompt = (
            f"Analyze the following technical document ('{doc.filename}') and extract the user's "
            "skills, programming languages, technologies, experience, completed projects, and learning goals.\n\n"
            f"Content:\n{doc.extracted_text[:6000]}\n\n"
            "Respond ONLY with a JSON object in this exact schema without extra commentary:\n"
            "{\n"
            '  "items": [\n'
            '    {"name": "Python", "category": "language", "level": "advanced"},\n'
            '    {"name": "FastAPI", "category": "technology", "level": "intermediate"},\n'
            '    {"name": "Distributed Systems", "category": "goal", "level": "beginner"}\n'
            "  ]\n"
            "}\n"
            "Allowed categories: skill, technology, language, experience, project, knowledge, goal.\n"
            "Allowed levels: beginner, intermediate, advanced, expert (or null)."
        )

        response = self._ai.chat(
            messages=[
                ChatMessage(
                    role="system",
                    content="You are a precise technical profile extractor. Extract genuine technical skills and experience without exaggerating mastery. Return strictly valid JSON.",
                ),
                ChatMessage(role="user", content=prompt),
            ]
        )

        raw_items = self._parse_json_items(response.content)
        saved_items: list[ProfileItem] = []

        existing_profile = self.get_profile(user_id)
        existing_names = {i.name.lower().strip() for i in existing_profile.items}

        for raw in raw_items:
            name = str(raw.get("name", "")).strip()
            cat = str(raw.get("category", "skill")).strip().lower()
            lvl = raw.get("level")
            if lvl is not None:
                lvl = str(lvl).strip().lower()
                if lvl not in {"beginner", "intermediate", "advanced", "expert"}:
                    lvl = None

            if not name or name.lower() in existing_names:
                continue

            item = ProfileItem(
                user_id=user_id,
                name=name,
                category=cat if cat in {"skill", "technology", "language", "experience", "project", "knowledge", "goal"} else "skill",
                level=lvl,
                is_confirmed=False,  # Unconfirmed until user approves
                source_type="document",
                source_id=document_id,
            )
            saved = self._repo.add_item(item)
            saved_items.append(saved)
            existing_names.add(name.lower())

        return saved_items

    @staticmethod
    def _parse_json_items(text: str) -> list[dict[str, Any]]:
        """Safely extract JSON object from LLM response."""
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                items = data.get("items", [])
                if isinstance(items, list):
                    return [i for i in items if isinstance(i, dict)]
            except json.JSONDecodeError:
                pass
        return []
