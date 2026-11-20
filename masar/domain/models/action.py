"""Domain models for AI tool actions and proposal workflows."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar

from masar.domain.exceptions.base import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)


@dataclass
class ProposedAction:
    """Represents a single atomic operation proposed by the AI assistant."""

    tool: str
    parameters: dict[str, Any]
    description: str = ""
    is_destructive: bool = False

    def __post_init__(self) -> None:
        if not self.tool or not self.tool.strip():
            raise EmptyFieldError("Proposed action tool name cannot be empty.")
        self.tool = self.tool.strip()
        if not isinstance(self.parameters, dict):
            raise ValidationError("Proposed action parameters must be a dictionary.")
        if not isinstance(self.description, str):
            self.description = str(self.description or "")
        self.description = self.description.strip()


@dataclass
class ActionResult:
    """Represents the outcome of executing a proposed action."""

    action_index: int
    tool: str
    status: str  # 'success' | 'failure'
    data: dict[str, Any] | None = None
    error: str | None = None

    VALID_STATUSES: ClassVar[set[str]] = {"success", "failure"}

    def __post_init__(self) -> None:
        if self.action_index < 0:
            raise ValidationError("Action index cannot be negative.")
        if not self.tool or not self.tool.strip():
            raise EmptyFieldError("Action result tool cannot be empty.")
        if self.status not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid action result status '{self.status}'. Must be one of: {sorted(self.VALID_STATUSES)}"
            )


@dataclass
class ActionProposal:
    """Represents a collection of proposed actions requiring user review and approval."""

    conversation_id: int
    user_id: int
    title: str
    actions: list[ProposedAction]
    status: str = "pending"
    results: list[ActionResult] = field(default_factory=list)
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    VALID_STATUSES: ClassVar[set[str]] = {
        "pending",
        "approved",
        "rejected",
        "executed",
        "failed",
    }
    MAX_TITLE_LENGTH: ClassVar[int] = 200

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate invariant rules for action proposals."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Action proposal ID must be a positive integer.")
        if self.conversation_id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Action proposal title cannot be empty.")
        self.title = self.title.strip()
        if len(self.title) > self.MAX_TITLE_LENGTH:
            raise FieldLengthError(
                f"Action proposal title cannot exceed {self.MAX_TITLE_LENGTH} characters."
            )
        if not isinstance(self.actions, list):
            raise ValidationError("Action proposal actions must be a list.")
        if not self.actions:
            raise ValidationError("Action proposal must contain at least one action.")
        if self.status not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid proposal status '{self.status}'. Must be one of: {sorted(self.VALID_STATUSES)}"
            )

    @property
    def has_destructive_actions(self) -> bool:
        """Check whether any proposed action in this proposal is destructive."""
        return any(action.is_destructive for action in self.actions)

    def approve(self) -> None:
        """Mark proposal as approved by user."""
        if self.status != "pending":
            raise ValidationError(f"Cannot approve proposal in '{self.status}' state.")
        self.status = "approved"

    def reject(self) -> None:
        """Mark proposal as rejected by user."""
        if self.status != "pending":
            raise ValidationError(f"Cannot reject proposal in '{self.status}' state.")
        self.status = "rejected"
        self.resolved_at = datetime.now(timezone.utc)

    def mark_executed(self, results: list[ActionResult]) -> None:
        """Mark proposal as executed successfully."""
        self.status = "executed"
        self.results = results
        self.resolved_at = datetime.now(timezone.utc)

    def mark_failed(self, results: list[ActionResult]) -> None:
        """Mark proposal as failed during execution."""
        self.status = "failed"
        self.results = results
        self.resolved_at = datetime.now(timezone.utc)
