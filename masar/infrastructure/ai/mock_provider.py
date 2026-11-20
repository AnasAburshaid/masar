"""Mock AI provider implementation for automated testing and offline verification."""

from typing import Any, Optional

from masar.application.interfaces.ai.ai_provider import AIProvider
from masar.domain.models.ai import AIResponse, AIUsage, ChatMessage


class MockAIProvider(AIProvider):
    """In-memory mock AI provider allowing predictable test verification without outbound network requests."""

    def __init__(
        self,
        default_response: str = "Mocked AI completion response",
        default_model: str = "mock-model-v1",
    ) -> None:
        self.default_response = default_response
        self.default_model = default_model
        self.response_queue: list[AIResponse] = []
        self.error_to_raise: Optional[Exception] = None
        self.recorded_calls: list[dict[str, Any]] = []

    def enqueue_response(self, content: str, *, model: Optional[str] = None) -> None:
        """Enqueue a specific response to be popped on the next call."""
        resp = AIResponse(
            content=content,
            model=model or self.default_model,
            usage=AIUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            finish_reason="stop",
        )
        self.response_queue.append(resp)

    def set_error(self, exc: Optional[Exception]) -> None:
        """Configure an exception to be raised on subsequent calls."""
        self.error_to_raise = exc

    def reset(self) -> None:
        """Reset all recorded calls, queued responses, and configured errors."""
        self.response_queue.clear()
        self.error_to_raise = None
        self.recorded_calls.clear()

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Record the completion call and return the next mocked response."""
        call_record = {
            "type": "complete",
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": model or self.default_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        self.recorded_calls.append(call_record)

        if self.error_to_raise is not None:
            raise self.error_to_raise

        if self.response_queue:
            return self.response_queue.pop(0)

        return AIResponse(
            content=self.default_response,
            model=model or self.default_model,
            usage=AIUsage(prompt_tokens=5, completion_tokens=15, total_tokens=20),
            finish_reason="stop",
        )

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Record the chat call and return the next mocked response."""
        call_record = {
            "type": "chat",
            "messages": messages,
            "model": model or self.default_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        self.recorded_calls.append(call_record)

        if self.error_to_raise is not None:
            raise self.error_to_raise

        if self.response_queue:
            return self.response_queue.pop(0)

        return AIResponse(
            content=self.default_response,
            model=model or self.default_model,
            usage=AIUsage(prompt_tokens=15, completion_tokens=25, total_tokens=40),
            finish_reason="stop",
        )
