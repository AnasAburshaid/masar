"""Tests for AIService and AI application schemas."""

import unittest
from pydantic import ValidationError as PydanticValidationError

from masar.application.schemas.ai import (
    AIResponseSchema,
    AIUsageSchema,
    ChatMessageSchema,
    ChatRequestSchema,
    CompletionRequestSchema,
)
from masar.application.services.ai_service import AIService
from masar.config.settings import Settings
from masar.container import build_ai_service
from masar.domain.exceptions.ai import AIRateLimitError
from masar.domain.exceptions.base import EmptyFieldError, ValidationError
from masar.domain.models.ai import AIResponse, AIUsage, ChatMessage
from masar.infrastructure.ai.mock_provider import MockAIProvider
from masar.infrastructure.ai.openrouter_provider import OpenRouterProvider


class TestAIService(unittest.TestCase):
    """Test suite for application-level AIService orchestration and validation."""

    def setUp(self) -> None:
        self.mock_provider = MockAIProvider(
            default_response="Default mock completion",
            default_model="mock-nemotron",
        )
        self.service = AIService(ai_provider=self.mock_provider)

    def test_complete_success(self) -> None:
        self.mock_provider.enqueue_response("Python learning plan created")
        response = self.service.complete(
            "Create a learning roadmap for Python",
            system_prompt="You are a senior tutor",
            model="custom-model",
            temperature=0.3,
            max_tokens=150,
        )

        self.assertIsInstance(response, AIResponse)
        self.assertEqual(response.content, "Python learning plan created")
        self.assertEqual(len(self.mock_provider.recorded_calls), 1)
        call = self.mock_provider.recorded_calls[0]
        self.assertEqual(call["type"], "complete")
        self.assertEqual(call["prompt"], "Create a learning roadmap for Python")
        self.assertEqual(call["system_prompt"], "You are a senior tutor")
        self.assertEqual(call["model"], "custom-model")
        self.assertEqual(call["temperature"], 0.3)
        self.assertEqual(call["max_tokens"], 150)

    def test_complete_empty_prompt_raises_empty_field_error(self) -> None:
        with self.assertRaises(EmptyFieldError):
            self.service.complete("")

        with self.assertRaises(EmptyFieldError):
            self.service.complete("   \n\t  ")

    def test_complete_propagates_provider_exception(self) -> None:
        self.mock_provider.set_error(AIRateLimitError("OpenRouter rate limit exceeded"))
        with self.assertRaises(AIRateLimitError):
            self.service.complete("Hello world")

    def test_chat_success(self) -> None:
        messages = [
            ChatMessage(role="system", content="You are a helpful coding assistant."),
            ChatMessage(role="user", content="How do decorators work in Python?"),
        ]
        self.mock_provider.enqueue_response("Decorators wrap functions.")

        response = self.service.chat(
            messages=messages,
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            temperature=0.5,
            max_tokens=200,
        )

        self.assertEqual(response.content, "Decorators wrap functions.")
        self.assertEqual(len(self.mock_provider.recorded_calls), 1)
        call = self.mock_provider.recorded_calls[0]
        self.assertEqual(call["type"], "chat")
        self.assertEqual(len(call["messages"]), 2)
        self.assertEqual(call["temperature"], 0.5)
        self.assertEqual(call["max_tokens"], 200)

    def test_chat_empty_messages_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.chat(messages=[])

    def test_chat_empty_content_in_message_raises_empty_field_error(self) -> None:
        with self.assertRaises(EmptyFieldError):
            self.service.chat(messages=[ChatMessage(role="user", content="   ")])

    def test_chat_invalid_role_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.chat(messages=[ChatMessage(role="invalid_role", content="Hello")])

    def test_chat_propagates_provider_error(self) -> None:
        self.mock_provider.set_error(AIRateLimitError("Quota limit hit"))
        with self.assertRaises(AIRateLimitError):
            self.service.chat(messages=[ChatMessage(role="user", content="Explain recursion")])

    def test_init_without_provider_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            AIService(ai_provider=None)  # type: ignore[arg-type]


class TestAIContainerWiring(unittest.TestCase):
    """Test dependency injection wiring for AI providers and services."""

    def test_build_ai_service_with_mock_provider(self) -> None:
        settings = Settings(ai_provider="mock", ai_model="mock-test-model")
        service = build_ai_service(settings=settings)
        self.assertIsInstance(service, AIService)
        response = service.complete("Ping")
        self.assertEqual(response.content, "Mocked AI completion response")
        self.assertEqual(response.model, "mock-test-model")

    def test_build_ai_service_with_openrouter_provider(self) -> None:
        settings = Settings(
            ai_provider="openrouter",
            ai_api_key="sk-or-test-key",
            ai_model="nvidia/nemotron-3-ultra-550b-a55b:free",
        )
        service = build_ai_service(settings=settings)
        self.assertIsInstance(service, AIService)
        self.assertIsInstance(service._provider, OpenRouterProvider)

    def test_build_ai_service_with_custom_provider_instance(self) -> None:
        custom_mock = MockAIProvider(default_response="Custom mock")
        service = build_ai_service(provider=custom_mock)
        self.assertIs(service._provider, custom_mock)
        self.assertEqual(service.complete("Test").content, "Custom mock")

    def test_build_ai_service_unknown_provider_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            build_ai_service(provider_type="unsupported_provider")


class TestAISchemas(unittest.TestCase):
    """Test suite for Pydantic AI DTO validation schemas."""

    def test_completion_request_schema_valid(self) -> None:
        schema = CompletionRequestSchema(
            prompt="  Write an outline for Docker mastery  ",
            system_prompt="Be concise",
            temperature=0.8,
            max_tokens=500,
        )
        self.assertEqual(schema.prompt, "Write an outline for Docker mastery")
        self.assertEqual(schema.system_prompt, "Be concise")
        self.assertEqual(schema.temperature, 0.8)
        self.assertEqual(schema.max_tokens, 500)

    def test_completion_request_schema_invalid_empty_prompt(self) -> None:
        with self.assertRaises(PydanticValidationError):
            CompletionRequestSchema(prompt="   ")

    def test_completion_request_schema_temperature_bounds(self) -> None:
        with self.assertRaises(PydanticValidationError):
            CompletionRequestSchema(prompt="Valid", temperature=-0.1)

        with self.assertRaises(PydanticValidationError):
            CompletionRequestSchema(prompt="Valid", temperature=2.5)

    def test_completion_request_schema_max_tokens_bounds(self) -> None:
        with self.assertRaises(PydanticValidationError):
            CompletionRequestSchema(prompt="Valid", max_tokens=0)

    def test_chat_message_schema_validation(self) -> None:
        msg = ChatMessageSchema(role="user", content="  Hello  ")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "Hello")

        with self.assertRaises(PydanticValidationError):
            ChatMessageSchema(role="admin", content="Hello")  # invalid role

        with self.assertRaises(PydanticValidationError):
            ChatMessageSchema(role="user", content="   ")  # empty content

    def test_chat_request_schema_validation(self) -> None:
        req = ChatRequestSchema(
            messages=[
                ChatMessageSchema(role="system", content="System instruction"),
                ChatMessageSchema(role="user", content="User query"),
            ],
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
        )
        self.assertEqual(len(req.messages), 2)
        self.assertEqual(req.model, "nvidia/nemotron-3-ultra-550b-a55b:free")

        with self.assertRaises(PydanticValidationError):
            ChatRequestSchema(messages=[])  # min_length=1

    def test_ai_response_schema_serialization(self) -> None:
        resp = AIResponseSchema(
            content="Generated answer",
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            usage=AIUsageSchema(prompt_tokens=15, completion_tokens=35, total_tokens=50),
            finish_reason="stop",
        )
        self.assertEqual(resp.content, "Generated answer")
        self.assertEqual(resp.usage.total_tokens, 50)


if __name__ == "__main__":
    unittest.main()
