"""Domain models and value objects for AI interactions."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChatMessage:
    """Represents a single chat message exchanged in an AI conversation."""

    role: str  # 'system', 'user', 'assistant'
    content: str

    def __post_init__(self) -> None:
        if not self.role or not self.role.strip():
            raise ValueError("ChatMessage role cannot be empty")
        if not isinstance(self.content, str):
            raise ValueError("ChatMessage content must be a string")


@dataclass(frozen=True)
class AIUsage:
    """Token consumption statistics reported by an AI provider."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class AIResponse:
    """Structured response returned by an AI provider."""

    content: str
    model: str
    usage: Optional[AIUsage] = None
    finish_reason: Optional[str] = None
