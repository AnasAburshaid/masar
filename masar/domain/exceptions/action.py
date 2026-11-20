"""Domain exceptions for AI tool calling and action proposals."""

from masar.domain.exceptions.base import (
    AccessDeniedError,
    DomainError,
    EntityNotFoundError,
    ValidationError,
)


class ActionError(DomainError):
    """Base exception for action proposal and tool execution errors."""

    pass


class UnknownToolError(ActionError, ValidationError):
    """Raised when an AI attempts to invoke an unrecognized or unregistered tool."""

    pass


class InvalidActionParametersError(ActionError, ValidationError):
    """Raised when proposed action parameters fail validation schemas."""

    pass


class ActionExecutionError(ActionError):
    """Raised when an action fails during backend execution."""

    pass


class ActionProposalNotFoundError(ActionError, EntityNotFoundError):
    """Raised when an action proposal is not found."""

    pass


class ActionProposalAlreadyResolvedError(ActionError, ValidationError):
    """Raised when an action proposal has already been approved, rejected, or executed."""

    pass


class ActionProposalAccessDeniedError(ActionError, AccessDeniedError):
    """Raised when a user attempts to access or execute another user's proposal."""

    pass
