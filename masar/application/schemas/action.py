"""Pydantic validation schemas for AI Tool Calling and Action Proposals."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProposedActionSchema(BaseModel):
    """Schema representing an individual proposed action."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    tool: str = Field(..., min_length=1, description="Name of the registered tool to invoke")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Parameters to pass to the tool")
    description: str = Field(default="", description="Human-readable description of what this action does")
    is_destructive: bool = Field(default=False, description="Flag indicating if action deletes data")


class ActionResultSchema(BaseModel):
    """Schema representing the outcome of executing a proposed action."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    action_index: int = Field(..., ge=0, description="Index of the executed action")
    tool: str = Field(..., min_length=1, description="Tool name that was executed")
    status: str = Field(..., description="'success' or 'failure'")
    data: Optional[dict[str, Any]] = Field(default=None, description="Output payload on success")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")


class ActionProposalCreateSchema(BaseModel):
    """Schema for creating a new action proposal."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200, description="Summary title of the proposal")
    actions: list[ProposedActionSchema] = Field(..., min_length=1, description="List of proposed actions to execute")


class ActionProposalResponseSchema(BaseModel):
    """Schema representing an action proposal in API responses."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    conversation_id: int
    user_id: int
    title: str
    status: str
    has_destructive_actions: bool = False
    actions: list[ProposedActionSchema] = Field(default_factory=list)
    results: list[ActionResultSchema] = Field(default_factory=list)
    created_at: datetime
    resolved_at: Optional[datetime] = None


class ActionApprovalResponseSchema(BaseModel):
    """Schema returned after a user approves and executes an action proposal."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    proposal: ActionProposalResponseSchema
    message: str
    executed_count: int
    failed_count: int
