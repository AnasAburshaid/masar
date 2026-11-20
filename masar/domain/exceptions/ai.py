"""Domain exceptions for AI operations and provider communication."""

from masar.domain.exceptions.base import DomainError


class AIError(DomainError):
    """Base exception for all AI operations."""


class AIConfigurationError(AIError):
    """Raised when the AI provider is misconfigured or missing credentials."""


class AIAuthenticationError(AIError):
    """Raised when AI provider authentication fails (e.g. invalid API key)."""


class AIRateLimitError(AIError):
    """Raised when an AI provider's rate limit or quota is exceeded."""


class AITimeoutError(AIError):
    """Raised when a request to an AI provider times out."""


class AIProviderError(AIError):
    """Raised when an upstream AI provider returns an error response."""
