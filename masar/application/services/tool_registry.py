"""Centralized registry for controlled AI tools."""

from dataclasses import dataclass
from typing import Any, Callable, NamedTuple

from masar.application.services.journey_service import JourneyService
from masar.application.services.note_service import NoteService
from masar.application.services.progress_service import ProgressService
from masar.application.services.section_service import SectionService
from masar.application.services.topic_service import TopicService
from masar.domain.exceptions.action import (
    InvalidActionParametersError,
    UnknownToolError,
)


class ServicesBundle(NamedTuple):
    """Bundle containing all application services required for tool execution."""

    journey_service: JourneyService
    section_service: SectionService
    topic_service: TopicService
    note_service: NoteService
    progress_service: ProgressService


@dataclass(frozen=True)
class ToolDefinition:
    """Metadata and execution handler for an individual AI tool."""

    name: str
    description: str
    parameters_schema: dict[str, Any]
    required_parameters: list[str]
    is_destructive: bool
    handler: Callable[[ServicesBundle, int, dict[str, Any]], dict[str, Any]]


def _handle_delete_journey(s: ServicesBundle, u: int, p: dict[str, Any]) -> dict[str, Any]:
    jid = int(p["journey_id"])
    s.journey_service.delete_journey(journey_id=jid, user_id=u)
    return {"deleted": True, "journey_id": jid}


def _handle_delete_section(s: ServicesBundle, u: int, p: dict[str, Any]) -> dict[str, Any]:
    sid = int(p["section_id"])
    s.section_service.delete_section(section_id=sid, user_id=u)
    return {"deleted": True, "section_id": sid}


def _handle_delete_topic(s: ServicesBundle, u: int, p: dict[str, Any]) -> dict[str, Any]:
    tid = int(p["topic_id"])
    s.topic_service.delete_topic(topic_id=tid, user_id=u)
    return {"deleted": True, "topic_id": tid}


def _handle_delete_note(s: ServicesBundle, u: int, p: dict[str, Any]) -> dict[str, Any]:
    nid = int(p["note_id"])
    s.note_service.delete_note(note_id=nid, user_id=u)
    return {"deleted": True, "note_id": nid}


class ToolRegistry:
    """Manages controlled tool definitions and executes actions via application services."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool definition."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition:
        """Retrieve a tool definition by name."""
        if name not in self._tools:
            raise UnknownToolError(f"Unrecognized tool '{name}'. Available: {sorted(self._tools.keys())}")
        return self._tools[name]

    def list_tools(self) -> list[ToolDefinition]:
        """Return all registered tool definitions."""
        return list(self._tools.values())

    def validate_action(self, tool_name: str, parameters: dict[str, Any]) -> None:
        """Validate that a tool exists and parameters satisfy requirements."""
        tool = self.get_tool(tool_name)
        for req in tool.required_parameters:
            if req not in parameters or parameters[req] is None or parameters[req] == "":
                raise InvalidActionParametersError(
                    f"Tool '{tool_name}' is missing required parameter '{req}'."
                )

    def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: int,
        services: ServicesBundle,
    ) -> dict[str, Any]:
        """Validate and execute a tool via the provided services bundle."""
        self.validate_action(tool_name, parameters)
        tool = self.get_tool(tool_name)
        return tool.handler(services, user_id, parameters)

    def get_tools_prompt_description(self) -> str:
        """Generate a concise textual overview of available tools for the AI system prompt."""
        lines = ["Available tools for creating learning data proposals:"]
        for tool in self.list_tools():
            dest_tag = " [DESTRUCTIVE]" if tool.is_destructive else ""
            params_str = ", ".join(
                f"{k}: {v.get('type', 'any')}{'*' if k in tool.required_parameters else ''}"
                for k, v in tool.parameters_schema.items()
            )
            lines.append(f"- {tool.name}({params_str}){dest_tag}: {tool.description}")
        return "\n".join(lines)

    def _register_default_tools(self) -> None:
        """Register the standard set of 17 application tools."""

        # ----------------- Journeys -----------------
        self.register(
            ToolDefinition(
                name="create_journey",
                description="Create a new learning journey.",
                parameters_schema={
                    "title": {"type": "string", "description": "Title of the learning roadmap"},
                    "description": {"type": "string", "description": "Detailed description of the roadmap"},
                },
                required_parameters=["title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "journey": {
                        "id": (j := s.journey_service.create_journey(
                            title=p["title"],
                            description=p.get("description", ""),
                            user_id=u,
                        )).id,
                        "title": j.title,
                        "description": j.description,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="list_journeys",
                description="List all learning journeys for the current user.",
                parameters_schema={},
                required_parameters=[],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "journeys": [
                        {"id": j.id, "title": j.title, "description": j.description}
                        for j in s.journey_service.list_journeys(user_id=u)
                    ]
                },
            )
        )

        self.register(
            ToolDefinition(
                name="get_journey",
                description="Retrieve details of a specific journey.",
                parameters_schema={"journey_id": {"type": "integer", "description": "ID of the journey"}},
                required_parameters=["journey_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "journey": {
                        "id": (j := s.journey_service.get_journey(int(p["journey_id"]), user_id=u)).id,
                        "title": j.title,
                        "description": j.description,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="update_journey",
                description="Update the title or description of an existing journey.",
                parameters_schema={
                    "journey_id": {"type": "integer", "description": "ID of the journey to update"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"},
                },
                required_parameters=["journey_id", "title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "journey": {
                        "id": (j := s.journey_service.update_journey(
                            journey_id=int(p["journey_id"]),
                            title=p["title"],
                            description=p.get("description", ""),
                            user_id=u,
                        )).id,
                        "title": j.title,
                        "description": j.description,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="delete_journey",
                description="Delete a learning journey and all its sections, topics, and notes.",
                parameters_schema={"journey_id": {"type": "integer", "description": "ID of the journey to delete"}},
                required_parameters=["journey_id"],
                is_destructive=True,
                handler=_handle_delete_journey,
            )
        )

        # ----------------- Sections -----------------
        self.register(
            ToolDefinition(
                name="create_section",
                description="Create a new section inside a learning journey.",
                parameters_schema={
                    "journey_id": {"type": "integer", "description": "ID of the parent journey"},
                    "title": {"type": "string", "description": "Title of the section"},
                },
                required_parameters=["journey_id", "title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "section": {
                        "id": (sec := s.section_service.create_section(
                            journey_id=int(p["journey_id"]),
                            title=p["title"],
                            user_id=u,
                        )).id,
                        "journey_id": sec.journey_id,
                        "title": sec.title,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="list_sections",
                description="List all sections in a journey.",
                parameters_schema={"journey_id": {"type": "integer", "description": "ID of the journey"}},
                required_parameters=["journey_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "sections": [
                        {"id": sec.id, "journey_id": sec.journey_id, "title": sec.title}
                        for sec in s.section_service.list_sections(int(p["journey_id"]), user_id=u)
                    ]
                },
            )
        )

        self.register(
            ToolDefinition(
                name="update_section",
                description="Rename an existing section.",
                parameters_schema={
                    "section_id": {"type": "integer", "description": "ID of the section to rename"},
                    "title": {"type": "string", "description": "New section title"},
                },
                required_parameters=["section_id", "title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "section": {
                        "id": (sec := s.section_service.rename_section(
                            section_id=int(p["section_id"]),
                            title=p["title"],
                            user_id=u,
                        )).id,
                        "journey_id": sec.journey_id,
                        "title": sec.title,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="delete_section",
                description="Delete a section and its topics and notes.",
                parameters_schema={"section_id": {"type": "integer", "description": "ID of the section to delete"}},
                required_parameters=["section_id"],
                is_destructive=True,
                handler=_handle_delete_section,
            )
        )

        # ----------------- Topics -----------------
        self.register(
            ToolDefinition(
                name="create_topic",
                description="Add a new topic to a section.",
                parameters_schema={
                    "section_id": {"type": "integer", "description": "ID of the section"},
                    "title": {"type": "string", "description": "Title of the learning topic"},
                },
                required_parameters=["section_id", "title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "topic": {
                        "id": (top := s.topic_service.create_topic(
                            section_id=int(p["section_id"]),
                            title=p["title"],
                            user_id=u,
                        )).id,
                        "section_id": top.section_id,
                        "title": top.title,
                        "is_completed": top.is_completed,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="list_topics",
                description="List all topics belonging to a section.",
                parameters_schema={"section_id": {"type": "integer", "description": "ID of the section"}},
                required_parameters=["section_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "topics": [
                        {
                            "id": top.id,
                            "section_id": top.section_id,
                            "title": top.title,
                            "is_completed": top.is_completed,
                        }
                        for top in s.topic_service.list_topics(int(p["section_id"]), user_id=u)
                    ]
                },
            )
        )

        self.register(
            ToolDefinition(
                name="update_topic",
                description="Rename an existing learning topic.",
                parameters_schema={
                    "topic_id": {"type": "integer", "description": "ID of the topic"},
                    "title": {"type": "string", "description": "New topic title"},
                },
                required_parameters=["topic_id", "title"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "topic": {
                        "id": (top := s.topic_service.rename_topic(
                            topic_id=int(p["topic_id"]),
                            title=p["title"],
                            user_id=u,
                        )).id,
                        "section_id": top.section_id,
                        "title": top.title,
                        "is_completed": top.is_completed,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="complete_topic",
                description="Mark a topic as completed.",
                parameters_schema={"topic_id": {"type": "integer", "description": "ID of the topic to mark complete"}},
                required_parameters=["topic_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "topic": {
                        "id": (top := s.topic_service.set_topic_completion(
                            topic_id=int(p["topic_id"]),
                            completed=True,
                            user_id=u,
                        )).id,
                        "title": top.title,
                        "is_completed": top.is_completed,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="pending_topic",
                description="Mark a completed topic back to pending.",
                parameters_schema={"topic_id": {"type": "integer", "description": "ID of the topic"}},
                required_parameters=["topic_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "topic": {
                        "id": (top := s.topic_service.set_topic_completion(
                            topic_id=int(p["topic_id"]),
                            completed=False,
                            user_id=u,
                        )).id,
                        "title": top.title,
                        "is_completed": top.is_completed,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="delete_topic",
                description="Delete a topic and its notes.",
                parameters_schema={"topic_id": {"type": "integer", "description": "ID of the topic to delete"}},
                required_parameters=["topic_id"],
                is_destructive=True,
                handler=_handle_delete_topic,
            )
        )

        # ----------------- Notes -----------------
        self.register(
            ToolDefinition(
                name="create_note",
                description="Attach a note or markdown summary to a topic.",
                parameters_schema={
                    "topic_id": {"type": "integer", "description": "ID of the topic"},
                    "content": {"type": "string", "description": "Content of the note"},
                },
                required_parameters=["topic_id", "content"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "note": {
                        "id": (n := s.note_service.create_note(
                            topic_id=int(p["topic_id"]),
                            content=p["content"],
                            user_id=u,
                        )).id,
                        "topic_id": n.topic_id,
                        "content": n.content,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="list_notes",
                description="List all notes attached to a topic.",
                parameters_schema={"topic_id": {"type": "integer", "description": "ID of the topic"}},
                required_parameters=["topic_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "notes": [
                        {"id": n.id, "topic_id": n.topic_id, "content": n.content}
                        for n in s.note_service.list_notes(int(p["topic_id"]), user_id=u)
                    ]
                },
            )
        )

        self.register(
            ToolDefinition(
                name="update_note",
                description="Update the content of an existing note.",
                parameters_schema={
                    "note_id": {"type": "integer", "description": "ID of the note to update"},
                    "content": {"type": "string", "description": "Updated note content"},
                },
                required_parameters=["note_id", "content"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "note": {
                        "id": (n := s.note_service.update_note(
                            note_id=int(p["note_id"]),
                            content=p["content"],
                            user_id=u,
                        )).id,
                        "topic_id": n.topic_id,
                        "content": n.content,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="delete_note",
                description="Delete a note by ID.",
                parameters_schema={"note_id": {"type": "integer", "description": "ID of the note to delete"}},
                required_parameters=["note_id"],
                is_destructive=True,
                handler=_handle_delete_note,
            )
        )

        # ----------------- Progress -----------------
        self.register(
            ToolDefinition(
                name="get_journey_progress",
                description="Retrieve calculated progress metrics for a journey.",
                parameters_schema={"journey_id": {"type": "integer", "description": "ID of the journey"}},
                required_parameters=["journey_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "progress": {
                        "completed_topics": (prog := s.progress_service.calculate_journey_progress(
                            journey_id=int(p["journey_id"]),
                            user_id=u,
                        )).completed_topics,
                        "total_topics": prog.total_topics,
                        "percentage": prog.percentage,
                    }
                },
            )
        )

        self.register(
            ToolDefinition(
                name="get_section_progress",
                description="Retrieve calculated progress metrics for a section.",
                parameters_schema={"section_id": {"type": "integer", "description": "ID of the section"}},
                required_parameters=["section_id"],
                is_destructive=False,
                handler=lambda s, u, p: {
                    "progress": {
                        "completed_topics": (prog := s.progress_service.calculate_section_progress(
                            section_id=int(p["section_id"]),
                            user_id=u,
                        )).completed_topics,
                        "total_topics": prog.total_topics,
                        "percentage": prog.percentage,
                    }
                },
            )
        )
