"""Abstract Base Class for AI/LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional

from masar.domain.models.ai import AIResponse, ChatMessage


class AIProvider(ABC):
    """Abstract interface defining the contract for AI/LLM providers."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate a text completion for a given prompt."""

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate a response in a multi-turn chat conversation."""
