"""OpenRouter / OpenAI-compatible LLM provider integration."""

import json
from typing import Any, Optional
import httpx

from masar.application.interfaces.ai.ai_provider import AIProvider
from masar.domain.exceptions.ai import (
    AIAuthenticationError,
    AIConfigurationError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
)
from masar.domain.models.ai import AIResponse, AIUsage, ChatMessage


class OpenRouterProvider(AIProvider):
    """Integrates with OpenRouter or OpenAI-compatible REST completion endpoints."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free",
        timeout_seconds: float = 30.0,
        default_temperature: float = 0.7,
        default_max_tokens: Optional[int] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._base_url = base_url.rstrip("/")
        self._default_model = default_model
        self._timeout_seconds = timeout_seconds
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens
        self._client = http_client

    def _ensure_api_key(self) -> None:
        if not self._api_key:
            raise AIConfigurationError(
                "AI API key is missing. Set OPENROUTER_API_KEY in your environment or .env file."
            )

    def _get_client(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        return httpx.Client(timeout=self._timeout_seconds)

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Execute a text completion formatted as a chat request."""
        messages: list[ChatMessage] = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))

        return self.chat(
            messages,
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
        """Send chat messages to the OpenRouter /chat/completions endpoint."""
        self._ensure_api_key()

        selected_model = model or self._default_model
        selected_temp = temperature if temperature is not None else self._default_temperature
        selected_max_tokens = max_tokens if max_tokens is not None else self._default_max_tokens

        payload: dict[str, Any] = {
            "model": selected_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": selected_temp,
        }
        if selected_max_tokens is not None:
            payload["max_tokens"] = selected_max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AnasAburshaid/masar",
            "X-Title": "Masar Learning Tracker",
        }

        endpoint = f"{self._base_url}/chat/completions"

        # Determine whether client is externally owned or locally instantiated
        external_client = self._client is not None
        client = self._get_client()

        try:
            response = client.post(endpoint, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise AITimeoutError(
                f"AI request timed out after {self._timeout_seconds}s: {exc}"
            ) from exc
        except httpx.RequestError as exc:
            raise AIProviderError(f"Network error communicating with AI provider: {exc}") from exc
        finally:
            if not external_client:
                client.close()

        # Parse HTTP response
        if response.status_code in (401, 403):
            raise AIAuthenticationError(
                f"AI authentication failed (HTTP {response.status_code}): {response.text}"
            )
        if response.status_code == 429:
            raise AIRateLimitError(
                f"AI rate limit or credit quota exceeded (HTTP 429): {response.text}"
            )
        if response.status_code >= 400:
            raise AIProviderError(
                f"AI provider returned error (HTTP {response.status_code}): {response.text}"
            )

        try:
            data = response.json()
            choice = data["choices"][0]
            content = choice["message"]["content"]
            response_model = data.get("model", selected_model)
            finish_reason = choice.get("finish_reason")

            usage: Optional[AIUsage] = None
            if "usage" in data and isinstance(data["usage"], dict):
                raw_usage = data["usage"]
                usage = AIUsage(
                    prompt_tokens=raw_usage.get("prompt_tokens", 0),
                    completion_tokens=raw_usage.get("completion_tokens", 0),
                    total_tokens=raw_usage.get("total_tokens", 0),
                )

            return AIResponse(
                content=content,
                model=response_model,
                usage=usage,
                finish_reason=finish_reason,
            )
        except (KeyError, IndexError, json.JSONDecodeError, TypeError) as exc:
            raise AIProviderError(
                f"Failed to parse AI provider response payload: {exc}"
            ) from exc
