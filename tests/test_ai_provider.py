"""Unit tests for AI providers (OpenRouterProvider and MockAIProvider)."""

import json
from typing import Any
import unittest
import httpx

from masar.domain.exceptions.ai import (
    AIAuthenticationError,
    AIConfigurationError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
)
from masar.domain.models.ai import AIResponse, ChatMessage
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.ai.openrouter_provider import OpenRouterProvider


class TestMockAIProvider(unittest.TestCase):
    """Test suite for MockAIProvider behavior."""

    def test_default_response_and_model(self) -> None:
        provider = MockAIProvider(default_response="Default answer", default_model="mock-v1")
        resp = provider.complete("Test prompt")
        self.assertEqual(resp.content, "Default answer")
        self.assertEqual(resp.model, "mock-v1")
        self.assertEqual(resp.usage.total_tokens, 20)

    def test_response_queue_fifo(self) -> None:
        provider = MockAIProvider()
        provider.enqueue_response("First queued response", model="model-a")
        provider.enqueue_response("Second queued response", model="model-b")

        r1 = provider.complete("Query 1")
        r2 = provider.complete("Query 2")
        r3 = provider.complete("Query 3")  # falls back to default

        self.assertEqual(r1.content, "First queued response")
        self.assertEqual(r1.model, "model-a")
        self.assertEqual(r2.content, "Second queued response")
        self.assertEqual(r2.model, "model-b")
        self.assertEqual(r3.content, "Mocked AI completion response")

    def test_set_error_and_reset(self) -> None:
        provider = MockAIProvider()
        provider.set_error(AITimeoutError("Simulated timeout"))

        with self.assertRaises(AITimeoutError):
            provider.complete("Should fail")

        provider.reset()
        self.assertEqual(len(provider.recorded_calls), 0)
        resp = provider.complete("Should succeed now")
        self.assertEqual(resp.content, "Mocked AI completion response")

    def test_recorded_calls(self) -> None:
        provider = MockAIProvider()
        provider.complete("Prompt 1", system_prompt="Sys 1", temperature=0.2)
        provider.chat(
            messages=[ChatMessage(role="user", content="Chat 1")],
            temperature=0.8,
            max_tokens=100,
        )

        self.assertEqual(len(provider.recorded_calls), 2)
        self.assertEqual(provider.recorded_calls[0]["type"], "complete")
        self.assertEqual(provider.recorded_calls[0]["prompt"], "Prompt 1")
        self.assertEqual(provider.recorded_calls[1]["type"], "chat")
        self.assertEqual(provider.recorded_calls[1]["max_tokens"], 100)


class TestOpenRouterProvider(unittest.TestCase):
    """Test suite for OpenRouterProvider with mocked HTTP transport."""

    def _create_mock_client(self, handler: Any) -> httpx.Client:
        transport = httpx.MockTransport(handler)
        return httpx.Client(transport=transport)

    def test_missing_api_key_raises_configuration_error(self) -> None:
        provider = OpenRouterProvider(api_key="")
        with self.assertRaises(AIConfigurationError):
            provider.complete("Test prompt")

        with self.assertRaises(AIConfigurationError):
            provider.chat(messages=[ChatMessage(role="user", content="Test")])

    def test_complete_success(self) -> None:
        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured_request["url"] = str(request.url)
            captured_request["headers"] = dict(request.headers)
            captured_request["body"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                status_code=200,
                json={
                    "id": "gen-test-123",
                    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Asyncio enables concurrent Python code.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 15,
                        "completion_tokens": 25,
                        "total_tokens": 40,
                    },
                },
            )

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(
            api_key="test-openrouter-key",
            default_model="nvidia/nemotron-3-ultra-550b-a55b:free",
            http_client=client,
        )

        resp = provider.complete(
            "Explain asyncio",
            system_prompt="Be concise",
            temperature=0.4,
            max_tokens=120,
        )

        self.assertIsInstance(resp, AIResponse)
        self.assertEqual(resp.content, "Asyncio enables concurrent Python code.")
        self.assertEqual(resp.model, "nvidia/nemotron-3-ultra-550b-a55b:free")
        self.assertEqual(resp.usage.total_tokens, 40)
        self.assertEqual(resp.finish_reason, "stop")

        # Verify request structure
        self.assertEqual(captured_request["url"], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(captured_request["headers"]["authorization"], "Bearer test-openrouter-key")
        body = captured_request["body"]
        self.assertEqual(body["model"], "nvidia/nemotron-3-ultra-550b-a55b:free")
        self.assertEqual(body["temperature"], 0.4)
        self.assertEqual(body["max_tokens"], 120)
        self.assertEqual(len(body["messages"]), 2)
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(body["messages"][0]["content"], "Be concise")
        self.assertEqual(body["messages"][1]["role"], "user")
        self.assertEqual(body["messages"][1]["content"], "Explain asyncio")

    def test_chat_success(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=200,
                json={
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "FastAPI is built on Starlette and Pydantic.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                },
            )

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        messages = [
            ChatMessage(role="user", content="What powers FastAPI?"),
        ]
        resp = provider.chat(messages=messages)
        self.assertEqual(resp.content, "FastAPI is built on Starlette and Pydantic.")

    def test_authentication_error_401(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=401,
                json={"error": {"message": "Invalid API key provided"}},
            )

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="invalid-key", http_client=client)

        with self.assertRaises(AIAuthenticationError) as ctx:
            provider.complete("Test")
        self.assertIn("Invalid API key provided", str(ctx.exception))

    def test_authentication_error_403(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=403, text="Forbidden access")

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="forbidden-key", http_client=client)

        with self.assertRaises(AIAuthenticationError):
            provider.complete("Test")

    def test_rate_limit_error_429(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=429,
                json={"error": {"message": "Free tier quota exhausted for this model"}},
            )

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        with self.assertRaises(AIRateLimitError) as ctx:
            provider.complete("Test")
        self.assertIn("quota exhausted", str(ctx.exception))

    def test_timeout_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("Request timed out after 30s")

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        with self.assertRaises(AITimeoutError):
            provider.complete("Test")

    def test_server_error_500(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=500,
                json={"error": {"message": "Internal upstream AI provider failure"}},
            )

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        with self.assertRaises(AIProviderError):
            provider.complete("Test")

    def test_malformed_response_json(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=200, json={"choices": []})

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        with self.assertRaises(AIProviderError):
            provider.complete("Test")

    def test_network_connection_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Failed to resolve host")

        client = self._create_mock_client(handler)
        provider = OpenRouterProvider(api_key="test-key", http_client=client)

        with self.assertRaises(AIProviderError):
            provider.complete("Test")


if __name__ == "__main__":
    unittest.main()
