"""Conversation service orchestrating multi-turn dialogues with Masar AI."""

import json
import re
from datetime import datetime, timezone
from typing import Any, Optional

from masar.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.application.interfaces.repositories.profile_repository import (
    ProfileRepository,
)
from masar.application.services.action_service import ActionService
from masar.application.services.ai_service import AIService
from masar.application.services.tool_registry import ServicesBundle
from masar.domain.exceptions.base import EmptyFieldError, InvalidIdError
from masar.domain.exceptions.conversation import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)
from masar.domain.models.action import ActionProposal, ProposedAction
from masar.domain.models.ai import ChatMessage
from masar.domain.models.conversation import Conversation, ConversationMessage

DEFAULT_SYSTEM_PROMPT = (
    "You are Masar AI, an intelligent personal technical learning mentor and engineering advisor.\n"
    "Your mission is to guide software engineers through complex technical disciplines with clarity, "
    "depth, empathy, and practical realism.\n\n"
    "### Mentorship Principles:\n"
    "1. Conversational & Empathetic: Communicate like an experienced senior engineer and dedicated personal mentor. "
    "Avoid robotic phrasing, generic canned intros (e.g., 'Hello! As an AI...'), repetitive apologies, or filler.\n"
    "2. Understand Before Prescribing: When a user asks to learn a new domain or build a roadmap, seek to understand "
    "their current background, goals, preferred focus, and weekly time commitment. If critical information is missing, "
    "ask one natural, focused clarifying question before generating an extensive plan. Do not ask questions if they already "
    "provided sufficient detail.\n"
    "3. Set Realistic Expectations: Never claim a developer can master large domains (e.g. Distributed Systems, Kubernetes, "
    "Compilers) in 1-2 weeks. Explain realistic multi-month timelines, core trade-offs, and necessary prerequisites.\n"
    "4. Clean Formatting: Format your conversational messages using polished, readable Markdown with clear headings, "
    "bullet points, bold highlights, code examples, and practical milestones.\n\n"
    "### Proposing Learning Plans & Application Actions:\n"
    "When you have sufficient understanding to create or modify a user's roadmap, you can propose concrete application changes.\n"
    "RULES FOR PROPOSALS:\n"
    "- NEVER expose raw tool names, JSON payloads, or technical schema details in your conversational message.\n"
    "- In your narrative message, explain the educational reasoning, structure of the sections, sequential topics, "
    "and hands-on practical exercises.\n"
    "- Append the proposal at the very end of your response inside a ```proposal code block:\n"
    "```proposal\n"
    "{\n"
    '  "action_proposal": {\n'
    '    "title": "<Human-readable title for the plan>",\n'
    '    "actions": [\n'
    '      {\n'
    '        "tool": "<tool_name>",\n'
    '        "description": "<Concise description of this action>",\n'
    '        "parameters": { ... },\n'
    '        "is_destructive": false\n'
    '      }\n'
    '    ]\n'
    '  }\n'
    "}\n"
    "```\n"
    "Available tools:\n"
    "- create_journey(title, description)\n"
    "- update_journey(journey_id, title, description)\n"
    "- delete_journey(journey_id) [destructive]\n"
    "- create_section(journey_id, title)\n"
    "- update_section(section_id, title)\n"
    "- delete_section(section_id) [destructive]\n"
    "- create_topic(section_id, title)\n"
    "- update_topic(topic_id, title)\n"
    "- complete_topic(topic_id)\n"
    "- pending_topic(topic_id)\n"
    "- delete_topic(topic_id) [destructive]\n"
    "- create_note(topic_id, content)\n"
    "- update_note(note_id, content)\n"
    "- delete_note(note_id) [destructive]\n"
    "- get_journey_progress(journey_id)\n"
    "- get_section_progress(section_id)\n\n"
    "You can chain multi-step actions by referencing created IDs with '$<index>.id' (e.g. '$0.id', '$1.id', '$prev.id').\n"
    "For learning roadmaps, create a comprehensive structure: 1 journey, multiple logical sections in learning order, "
    "granular topics per section, and attach practical exercise notes to key topics.\n\n"
    "### Adaptive Learning Tracking & Recommendations:\n"
    "1. Actual Progress Visibility: You have real-time visibility into the user's active journeys, completion percentages, topics, notes, and personal knowledge profile.\n"
    "2. Discussing Topics & Difficulties: When the developer discusses completed topics or concepts they struggle with, identify potential knowledge gaps, prerequisite deficiencies, or unnecessary repetition. Recommend what to study next and explain the pedagogical reasoning.\n"
    "3. Strict Human-in-the-Loop Integrity: NEVER mark a topic as completed autonomously merely because the user asked a question or discussed it. All progress updates and journey modifications must be user-confirmed or proposed through action proposals for review.\n"
    "4. Proposing Journey Improvements: Propose concrete updates (new topics, prerequisite sections, refresher notes) via action proposals with clear explanations of why they improve the learning plan."
)


class ConversationService:
    """Coordinates conversational workflows, message persistence, and AI responses."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        ai_service: AIService,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        action_service: Optional[ActionService] = None,
        services_bundle: Optional[ServicesBundle] = None,
        document_repository: Optional[DocumentRepository] = None,
        profile_repository: Optional[ProfileRepository] = None,
    ) -> None:
        self._repo = conversation_repository
        self._ai = ai_service
        self._system_prompt = system_prompt
        self._action_service = action_service
        self._services_bundle = services_bundle
        self._document_repo = document_repository
        self._profile_repo = profile_repository

    def _build_user_context(self, user_id: int) -> str:
        """Construct a real-time contextual snapshot of the user's existing learning roadmaps."""
        if not self._services_bundle:
            return ""

        journeys = self._services_bundle.journey_service.list_journeys(user_id=user_id)
        if not journeys:
            return "User currently has no existing learning journeys in Masar."

        lines = ["### User's Current Learning Roadmaps in Masar:"]
        for j in journeys:
            desc = f" ({j.description})" if j.description else ""
            prog = self._services_bundle.progress_service.calculate_journey_progress(j.id or 1, user_id=user_id)
            lines.append(f"- Journey #{j.id}: '{j.title}'{desc} [{prog.percentage:.0f}% completed ({prog.completed_topics}/{prog.total_topics} topics)]")
            sections = self._services_bundle.section_service.list_sections(journey_id=j.id or 1, user_id=user_id)
            for s in sections:
                topics = self._services_bundle.topic_service.list_topics(section_id=s.id or 1, user_id=user_id)
                topic_summaries = [f"'{t.title}'" + (" [completed]" if t.is_completed else "") for t in topics]
                topic_str = f" (Topics: {', '.join(topic_summaries)})" if topic_summaries else " (No topics yet)"
                lines.append(f"  * Section #{s.id}: '{s.title}'{topic_str}")

        if self._profile_repo:
            profile = self._profile_repo.get_profile(user_id)
            if profile.items or profile.bio:
                lines.append("\n### User's Personal Knowledge Profile:")
                if profile.bio:
                    lines.append(f"Background Bio: {profile.bio}")
                confirmed = profile.confirmed_items
                if confirmed:
                    skill_parts = [f"{i.name} ({i.level})" if i.level else i.name for i in confirmed]
                    lines.append(f"- User-Confirmed Skills & Knowledge (Proven): {', '.join(skill_parts)}")
                inferred = profile.inferred_items
                if inferred:
                    inferred_parts = [f"{i.name} ({i.level})" if i.level else i.name for i in inferred]
                    lines.append(f"- AI-Inferred Skills (Needs Confirmation): {', '.join(inferred_parts)}")
                goals = [i.name for i in profile.items if i.category == "goal"]
                if goals:
                    lines.append(f"- Stated Learning Goals & Focus: {', '.join(goals)}")

        return "\n".join(lines)

    def create_conversation(
        self, user_id: int, title: Optional[str] = None
    ) -> Conversation:
        """Create and persist a new conversation for an authenticated user."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        resolved_title = title.strip() if title and title.strip() else "New Conversation"
        conv = Conversation(user_id=user_id, title=resolved_title)
        return self._repo.add_conversation(conv)

    def list_conversations(self, user_id: int) -> list[Conversation]:
        """List all conversations for a specific user ordered by latest activity."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        return self._repo.get_conversations_by_user_id(user_id)

    def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> tuple[Conversation, list[ConversationMessage]]:
        """Retrieve a conversation and its messages, enforcing user ownership."""
        conv = self._verify_ownership(conversation_id, user_id)
        messages = self._repo.get_messages_by_conversation_id(conversation_id)
        return conv, messages

    def update_title(
        self, conversation_id: int, user_id: int, title: str
    ) -> Conversation:
        """Update a conversation's title."""
        conv = self._verify_ownership(conversation_id, user_id)
        conv.update_title(title)
        return self._repo.update_conversation(conv)

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and its associated messages."""
        self._verify_ownership(conversation_id, user_id)
        return self._repo.delete_conversation(conversation_id)

    def send_message(
        self,
        conversation_id: int,
        user_id: int,
        content: str,
        document_id: Optional[int] = None,
    ) -> tuple[ConversationMessage, ConversationMessage, Optional[ActionProposal]]:
        """Record user message, dispatch multi-turn dialogue to AI, and persist response."""
        conv = self._verify_ownership(conversation_id, user_id)

        if not content or not content.strip():
            raise EmptyFieldError("Message content cannot be empty.")
        clean_content = content.strip()

        # 1. Persist the user's incoming message
        user_msg = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=clean_content,
        )
        saved_user_msg = self._repo.add_message(user_msg)

        # 2. Automatically generate title if still default
        if conv.title == "New Conversation":
            first_line = clean_content.split("\n")[0][:45].strip()
            new_title = f"{first_line}..." if len(clean_content) > 45 else first_line
            conv.update_title(new_title or "Learning Chat")
            self._repo.update_conversation(conv)

        # 3. Retrieve conversation history for multi-turn context
        all_messages = self._repo.get_messages_by_conversation_id(conversation_id)

        # 4. Construct ChatMessage dialogue with system instructions and user context
        user_context = self._build_user_context(user_id)
        effective_system_prompt = self._system_prompt
        if user_context:
            effective_system_prompt = f"{effective_system_prompt}\n\n{user_context}"

        # Inject attached document context if provided
        if document_id is not None and self._document_repo is not None:
            doc = self._document_repo.get_by_id(document_id)
            if doc and doc.user_id == user_id:
                content_excerpt = doc.extracted_text[:6000]
                summary_excerpt = f"Summary: {doc.summary}\n" if doc.summary else ""
                effective_system_prompt = (
                    f"{effective_system_prompt}\n\n"
                    f"### Attached Document Context ('{doc.filename}', Type: {doc.file_type}):\n"
                    f"{summary_excerpt}"
                    f"Content Excerpt:\n{content_excerpt}\n"
                    f"### End Attached Document"
                )

        dialogue: list[ChatMessage] = [
            ChatMessage(role="system", content=effective_system_prompt)
        ]
        for m in all_messages:
            dialogue.append(ChatMessage(role=m.role, content=m.content))

        # 5. Call AI Service
        ai_response = self._ai.chat(messages=dialogue)

        # 6. Extract any action proposals embedded in the AI response
        cleaned_content, proposal_data = self._extract_action_proposal(ai_response.content)

        proposal: Optional[ActionProposal] = None
        if proposal_data and self._action_service is not None:
            raw_actions = proposal_data.get("actions", [])
            proposed_actions = [
                ProposedAction(
                    tool=a["tool"],
                    parameters=a.get("parameters", {}),
                    description=a.get("description", ""),
                    is_destructive=bool(a.get("is_destructive", False)),
                )
                for a in raw_actions
                if isinstance(a, dict) and "tool" in a
            ]
            if proposed_actions:
                proposal = self._action_service.create_proposal(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    title=proposal_data.get("title", "Proposed Actions"),
                    actions=proposed_actions,
                )

        # 7. Persist assistant reply
        assistant_msg = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=cleaned_content,
        )
        saved_assistant_msg = self._repo.add_message(assistant_msg)

        # 8. Bump conversation updated_at
        conv.updated_at = datetime.now(timezone.utc)
        self._repo.update_conversation(conv)

        return saved_user_msg, saved_assistant_msg, proposal

    def _extract_action_proposal(self, content: str) -> tuple[str, Optional[dict[str, Any]]]:
        """Extract action_proposal block from response content and return cleaned message text."""
        # Check for action_proposal keyword
        keyword = '"action_proposal"'
        kw_pos = content.find(keyword)
        if kw_pos == -1:
            keyword = "'action_proposal'"
            kw_pos = content.find(keyword)

        if kw_pos != -1:
            raw_json, json_start, json_end = self._find_balanced_json(content, kw_pos)
            if raw_json:
                try:
                    parsed = json.loads(raw_json)
                    if isinstance(parsed, dict) and "action_proposal" in parsed:
                        proposal_obj = parsed["action_proposal"]

                        # Determine boundaries to remove including markdown fences if wrapped
                        remove_start = json_start
                        remove_end = json_end

                        # Expand backwards to include ```json or ```proposal or ```
                        prefix = content[:remove_start]
                        fence_match = re.search(r"```(?:json|proposal)?\s*$", prefix)
                        if fence_match:
                            remove_start = fence_match.start()

                        # Expand forwards to include closing ```
                        suffix = content[remove_end:]
                        close_fence_match = re.match(r"^\s*```", suffix)
                        if close_fence_match:
                            remove_end = remove_end + close_fence_match.end()

                        cleaned = (content[:remove_start] + content[remove_end:]).strip()
                        # Extra cleanup: remove any leftover empty fences or json artifacts
                        cleaned = re.sub(r"```(?:json|proposal)?\s*```", "", cleaned).strip()
                        return cleaned, proposal_obj
                except json.JSONDecodeError:
                    pass

        # Fallback to regex patterns if balanced finder was outside standard structure
        code_block_pattern = r"```(?:json|proposal)?\s*(\{\s*[\"']action_proposal[\"'][\s\S]*?\})\s*```"
        match = re.search(code_block_pattern, content)
        if match:
            raw_json = match.group(1)
            try:
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict) and "action_proposal" in parsed:
                    cleaned = re.sub(code_block_pattern, "", content).strip()
                    return cleaned, parsed["action_proposal"]
            except json.JSONDecodeError:
                pass

        return content.strip(), None

    @staticmethod
    def _find_balanced_json(text: str, start_index: int) -> tuple[Optional[str], int, int]:
        """Find balanced JSON object containing start_index.
        Returns (json_str, start_pos, end_pos) or (None, -1, -1)."""
        brace_start = text.rfind("{", 0, start_index + 1)
        if brace_start == -1:
            brace_start = text.find("{", start_index)
            if brace_start == -1:
                return None, -1, -1

        depth = 0
        in_string = False
        escape = False

        for i in range(brace_start, len(text)):
            char = text[i]
            if escape:
                escape = False
                continue
            if char == "\\":
                if in_string:
                    escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return text[brace_start : i + 1], brace_start, i + 1
        return None, -1, -1

    def _verify_ownership(self, conversation_id: int, user_id: int) -> Conversation:
        """Ensure the conversation exists and belongs to the requested user."""
        if conversation_id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        conv = self._repo.get_conversation_by_id(conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found."
            )
        if conv.user_id != user_id:
            raise ConversationAccessDeniedError(
                f"User {user_id} does not have access to conversation {conversation_id}."
            )
        return conv
