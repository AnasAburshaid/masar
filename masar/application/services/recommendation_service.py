"""Adaptive learning recommendations and knowledge gap analysis service."""

from typing import Any, Optional
import json
import re

from masar.application.services.ai_service import AIService
from masar.application.services.journey_service import JourneyService
from masar.application.services.note_service import NoteService
from masar.application.services.profile_service import ProfileService
from masar.application.services.progress_service import ProgressService
from masar.application.services.section_service import SectionService
from masar.application.services.topic_service import TopicService
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.models.ai import ChatMessage
from masar.domain.models.recommendation import (
    AdaptiveLearningSummary,
    KnowledgeGap,
    Recommendation,
)


class RecommendationService:
    """Service generating adaptive study recommendations, next steps, and gap detection."""

    def __init__(
        self,
        journey_service: JourneyService,
        section_service: SectionService,
        topic_service: TopicService,
        note_service: NoteService,
        progress_service: ProgressService,
        profile_service: Optional[ProfileService] = None,
        ai_service: Optional[AIService] = None,
    ) -> None:
        self._journey_service = journey_service
        self._section_service = section_service
        self._topic_service = topic_service
        self._note_service = note_service
        self._progress_service = progress_service
        self._profile_service = profile_service
        self._ai_service = ai_service

    def get_recommendations(
        self, user_id: int, journey_id: Optional[int] = None
    ) -> AdaptiveLearningSummary:
        """Analyze learning progress, notes, and profile to compute adaptive recommendations."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        # 1. Fetch user's journeys
        all_journeys = self._journey_service.list_journeys(user_id=user_id)
        if journey_id is not None:
            journeys = [j for j in all_journeys if j.id == journey_id]
        else:
            journeys = all_journeys

        total_completed = 0
        total_in_progress = 0
        active_titles: list[str] = []
        recommendations: list[Recommendation] = []
        knowledge_gaps: list[KnowledgeGap] = []

        all_topic_names: set[str] = set()

        for journey in journeys:
            if journey.id is None:
                continue

            active_titles.append(journey.title)
            progress = self._progress_service.calculate_journey_progress(journey.id, user_id=user_id)
            total_completed += progress.completed_topics
            total_in_progress += (progress.total_topics - progress.completed_topics)

            sections = self._section_service.list_sections(journey_id=journey.id, user_id=user_id)
            next_topic_found_for_journey = False

            for section in sections:
                if section.id is None:
                    continue
                topics = self._topic_service.list_topics(section_id=section.id, user_id=user_id)

                for topic in topics:
                    all_topic_names.add(topic.title.lower().strip())

                    # Check notes on topic for difficulty flags
                    if topic.id is not None:
                        notes = self._note_service.list_notes(topic_id=topic.id, user_id=user_id)
                        for note in notes:
                            note_lower = note.content.lower()
                            if any(
                                w in note_lower
                                for w in ("difficult", "confused", "stuck", "hard", "revisit", "todo")
                            ):
                                recommendations.append(
                                    Recommendation(
                                        title=f"Review and reinforce '{topic.title}'",
                                        reason=(
                                            f"Your personal study notes on '{topic.title}' mention difficulties "
                                            f"or items to revisit: \"{note.content[:120]}...\". Solidifying this will "
                                            "prevent compounding knowledge gaps."
                                        ),
                                        recommendation_type="review_refresher",
                                        journey_id=journey.id,
                                        journey_title=journey.title,
                                        section_id=section.id,
                                        suggested_action="add_note",
                                        action_payload={"topic_id": topic.id},
                                        confidence=0.9,
                                    )
                                )

                    # Recommend the immediate next pending topic
                    if not topic.is_completed and not next_topic_found_for_journey:
                        next_topic_found_for_journey = True
                        recommendations.append(
                            Recommendation(
                                title=f"Study '{topic.title}' in {journey.title}",
                                reason=(
                                    f"This is the immediate next incomplete topic in section '{section.title}'. "
                                    f"Completing it advances '{journey.title}' toward completion ({progress.percentage:.0f}% current progress)."
                                ),
                                recommendation_type="next_topic",
                                journey_id=journey.id,
                                journey_title=journey.title,
                                section_id=section.id,
                                suggested_action="study_next",
                                action_payload={"topic_id": topic.id, "title": topic.title},
                                confidence=0.95,
                            )
                        )

            # Capstone or milestone completion
            if progress.total_topics > 0 and progress.percentage >= 100.0:
                recommendations.append(
                    Recommendation(
                        title=f"Build a Capstone Project for '{journey.title}'",
                        reason=(
                            f"Congratulations! You have completed all {progress.total_topics} topics in '{journey.title}'. "
                            "Applying your knowledge in an end-to-end practical project is the best way to retain long-term mastery."
                        ),
                        recommendation_type="review_refresher",
                        journey_id=journey.id,
                        journey_title=journey.title,
                        confidence=0.85,
                    )
                )

        # 2. Correlate with Personal Learning Profile & Goals
        if self._profile_service is not None:
            profile = self._profile_service.get_profile(user_id)
            for item in profile.items:
                # Goal not covered in any journey
                if item.category == "goal":
                    if not any(item.name.lower() in t for t in all_topic_names):
                        knowledge_gaps.append(
                            KnowledgeGap(
                                topic_name=item.name,
                                description=(
                                    f"You designated '{item.name}' as a key learning goal in your profile, "
                                    "but none of your current roadmaps explicitly teach this subject."
                                ),
                                remedy=f"Create a new learning journey or add a dedicated section covering '{item.name}'.",
                            )
                        )
                        recommendations.append(
                            Recommendation(
                                title=f"Create a Roadmap for goal '{item.name}'",
                                reason=(
                                    f"You have '{item.name}' listed as an active goal in your profile. Adding dedicated "
                                    "milestones will help you systematically achieve it."
                                ),
                                recommendation_type="journey_update",
                                suggested_action="create_journey",
                                action_payload={"title": f"{item.name} Learning Track"},
                                confidence=0.9,
                            )
                        )

                # Unconfirmed AI skills needing validation
                elif not item.is_confirmed and item.source_type == "document":
                    recommendations.append(
                        Recommendation(
                            title=f"Review inferred skill '{item.name}'",
                            reason=(
                                f"Extracted from your uploaded document. Confirming whether you have {item.level or 'experience'} "
                                "in this technology enables your AI mentor to tune explanations to your exact level."
                            ),
                            recommendation_type="prerequisite",
                            confidence=0.8,
                        )
                    )

        # Deduplicate recommendations by title
        seen_titles: set[str] = set()
        unique_recommendations: list[Recommendation] = []
        for r in recommendations:
            if r.title.lower() not in seen_titles:
                seen_titles.add(r.title.lower())
                unique_recommendations.append(r)

        return AdaptiveLearningSummary(
            user_id=user_id,
            total_completed_topics=total_completed,
            total_in_progress_topics=total_in_progress,
            active_journey_titles=active_titles,
            knowledge_gaps=knowledge_gaps,
            recommendations=unique_recommendations[:10],
        )

    def propose_journey_improvement(
        self, user_id: int, journey_id: int, feedback: str
    ) -> list[Recommendation]:
        """Propose specific topics or sections to add to a journey based on learning feedback."""
        if user_id <= 0 or journey_id <= 0:
            raise InvalidIdError("User ID and Journey ID must be positive integers.")

        journey = self._journey_service.get_journey(journey_id, user_id=user_id)
        sections = self._section_service.list_sections(journey_id=journey_id, user_id=user_id)
        default_section_id = sections[0].id if sections and sections[0].id is not None else None

        if self._ai_service is None:
            # Fallback algorithmic heuristic
            return [
                Recommendation(
                    title=f"Add prerequisite topic for '{feedback[:40]}'",
                    reason="Based on your feedback, breaking down complex prerequisites into smaller milestones will improve retention.",
                    recommendation_type="journey_update",
                    journey_id=journey_id,
                    journey_title=journey.title,
                    section_id=default_section_id,
                    suggested_action="create_topic",
                    action_payload={
                        "section_id": default_section_id,
                        "title": f"Fundamentals of {feedback[:30]}",
                    },
                    confidence=0.8,
                )
            ]

        # Use AI to generate intelligent, reasoned improvements
        existing_topic_titles = [
            t.title
            for s in sections
            if s.id is not None
            for t in self._topic_service.list_topics(section_id=s.id, user_id=user_id)
        ]

        prompt = (
            f"User is studying '{journey.title}'.\n"
            f"Existing topics in roadmap: {', '.join(existing_topic_titles[:25])}\n"
            f"User feedback/difficulty: \"{feedback}\"\n\n"
            "Suggest 1-3 targeted new topics or updates to improve this learning journey. "
            "For each suggestion, provide a concise title and a clear pedagogical explanation of why it helps.\n"
            "Respond ONLY with a JSON object in this schema:\n"
            "{\n"
            '  "improvements": [\n'
            '    {"title": "Suggested Topic Name", "reason": "Explanation of pedagogical benefit."}\n'
            "  ]\n"
            "}"
        )

        ai_resp = self._ai_service.chat(
            messages=[
                ChatMessage(
                    role="system",
                    content="You are a senior curriculum architect. Propose structured, highly relevant learning topics with sound rationale. Return strictly valid JSON.",
                ),
                ChatMessage(role="user", content=prompt),
            ]
        )

        proposals = self._parse_json_improvements(ai_resp.content)
        result: list[Recommendation] = []

        for p in proposals:
            title = str(p.get("title", "")).strip()
            reason = str(p.get("reason", "")).strip()
            if not title or not reason:
                continue

            result.append(
                Recommendation(
                    title=title,
                    reason=reason,
                    recommendation_type="journey_update",
                    journey_id=journey_id,
                    journey_title=journey.title,
                    section_id=default_section_id,
                    suggested_action="create_topic",
                    action_payload={
                        "section_id": default_section_id,
                        "title": title,
                    },
                    confidence=0.9,
                )
            )

        return result

    @staticmethod
    def _parse_json_improvements(text: str) -> list[dict[str, Any]]:
        """Safely extract improvements list from AI JSON completion."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                items = data.get("improvements", [])
                if isinstance(items, list):
                    return [i for i in items if isinstance(i, dict)]
            except json.JSONDecodeError:
                pass
        return []
