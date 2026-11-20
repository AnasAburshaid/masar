"""Application service coordinating AI interactions."""

from typing import Optional

from masar.application.interfaces.ai.ai_provider import AIProvider
from masar.domain.exceptions.base import EmptyFieldError, ValidationError
from masar.domain.models.ai import AIResponse, ChatMessage


class AIService:
    """Coordinates AI provider interactions for text completion and chat dialogues."""

    def __init__(
        self,
        ai_provider: Optional[AIProvider] = None,
        *,
        provider: Optional[AIProvider] = None,
    ) -> None:
        target = ai_provider or provider
        if target is None:
            raise ValueError("An AIProvider instance must be provided to AIService.")
        self._provider = target

    def complete(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Validate and dispatch a text completion request."""
        if not prompt or not prompt.strip():
            raise EmptyFieldError("Prompt cannot be empty")

        return self._provider.complete(
            prompt.strip(),
            system_prompt=system_prompt.strip() if system_prompt else None,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Validate and dispatch a multi-turn chat request."""
        if not messages:
            raise ValidationError("Messages list cannot be empty")

        valid_roles = {"system", "user", "assistant"}
        for msg in messages:
            if not msg.role or msg.role not in valid_roles:
                raise ValidationError(
                    f"Invalid message role '{msg.role}'. Must be one of: {sorted(valid_roles)}"
                )
            if not msg.content or not msg.content.strip():
                raise EmptyFieldError("Chat message content cannot be empty")

        return self._provider.chat(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
