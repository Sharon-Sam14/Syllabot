"""
backend/tests/test_ai_refactor.py

Unit tests validating serialization, conversation normalisation,
provider adapters, health cache cooldowns, and LLMService fallbacks.
"""
import pytest
import time
from unittest.mock import patch, MagicMock

from backend.ai.providers.base import (
    Message,
    ToolCall,
    ProviderResponse,
    RateLimitError,
    QuotaExceededError,
    RetryableError,
    ValidationError,
    AuthenticationError,
    ProviderError,
)
from backend.core.serializer import MessageSerializer, ToolMessageBuilder, ConversationNormalizer
from backend.ai.providers.router import ModelRouter
from backend.ai.providers.gemini import GeminiProvider
from backend.ai.providers.groq import GroqProvider
from backend.ai.services import LLMService, LLMServiceException


# ── 1. Message Serializer Tests ───────────────────────────────────────────────

class TestMessageSerializer:
    def test_serialize_deserialize_simple(self):
        msg = Message(role="user", content="hello world")
        serialized = MessageSerializer.to_dict(msg)
        assert serialized == {"role": "user", "content": "hello world"}

        deserialized = MessageSerializer.from_dict(serialized)
        assert deserialized.role == "user"
        assert deserialized.content == "hello world"
        assert deserialized.tool_calls is None

    def test_serialize_deserialize_tool_calls(self):
        msg = Message(
            role="assistant",
            content=None,
            tool_calls=[ToolCall(id="call_123", name="generate_quiz", arguments={"plan_id": 1})]
        )
        serialized = MessageSerializer.to_dict(msg)
        assert serialized["role"] == "assistant"
        assert serialized["tool_calls"] == [{"id": "call_123", "name": "generate_quiz", "arguments": {"plan_id": 1}}]

        deserialized = MessageSerializer.from_dict(serialized)
        assert deserialized.role == "assistant"
        assert len(deserialized.tool_calls) == 1
        assert deserialized.tool_calls[0].id == "call_123"
        assert deserialized.tool_calls[0].name == "generate_quiz"
        assert deserialized.tool_calls[0].arguments == {"plan_id": 1}


# ── 2. Conversation Normalizer Tests ──────────────────────────────────────────

class TestConversationNormalizer:
    def test_relink_missing_tool_call_id(self):
        history = [
            {
                "role": "user",
                "content": "Give me a quiz"
            },
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{"id": "tc_01", "name": "generate_quiz", "arguments": {"plan_id": 1}}]
            },
            {
                "role": "tool",
                "name": "generate_quiz",
                "content": '{"status": "success"}'
                # Missing tool_call_id!
            }
        ]

        normalized = ConversationNormalizer.normalize(history)
        assert len(normalized) == 3
        # Check that the tool message was correctly linked to "tc_01"
        assert normalized[2].role == "tool"
        assert normalized[2].tool_call_id == "tc_01"

    def test_validation_error_on_bad_role(self):
        history = [{"role": "hacker", "content": "inject prompt"}]
        with pytest.raises(ValidationError):
            ConversationNormalizer.normalize(history)


# ── 3. Health Cache & Cooldown Tests ──────────────────────────────────────────

class TestModelRouterHealth:
    def test_mark_unhealthy_and_cooldown(self):
        router = ModelRouter()
        
        # Initially healthy
        assert router.is_healthy("gemini") is True

        # Mark unhealthy for 60 seconds
        router.mark_unhealthy("gemini", cooldown_seconds=60.0)
        assert router.is_healthy("gemini") is False

        # Fast forward time to check recovery
        future_time = time.time() + 61.0
        with patch("time.time", return_value=future_time):
            assert router.is_healthy("gemini") is True

    def test_fallback_routing_when_unhealthy(self):
        router = ModelRouter()
        # Mock providers to say both are configured and available
        router._gemini.is_available = MagicMock(return_value=True)
        router._groq.is_available = MagicMock(return_value=True)
        
        # When Gemini is healthy, task "general_chat" routes to Gemini
        assert router.get_provider_for_task("general_chat").name == "gemini"

        # Mark Gemini unhealthy
        router.mark_unhealthy("gemini", cooldown_seconds=60.0)
        # Should now route to Groq fallback
        assert router.get_provider_for_task("general_chat").name == "groq"


# ── 4. Provider Adapter Mapping Tests ─────────────────────────────────────────

class TestGeminiAdapter:
    def test_prepare_messages_gemini(self):
        provider = GeminiProvider()
        messages = [
            Message(role="user", content="hi"),
            Message(
                role="assistant",
                content=None,
                tool_calls=[ToolCall(id="tc_1", name="get_topics", arguments={})]
            ),
            Message(role="tool", content="{}", tool_call_id="tc_1")
        ]
        
        lc_msgs = provider.prepare_messages(messages, system_prompt="be helpful")
        assert len(lc_msgs) == 4 # system + user + assistant + tool
        assert lc_msgs[0].content == "be helpful"
        assert lc_msgs[1].content == "hi"
        assert lc_msgs[2].tool_calls == [{"id": "tc_1", "name": "get_topics", "args": {}, "type": "tool_call"}]
        assert lc_msgs[3].tool_call_id == "tc_1"

    def test_error_classification_gemini(self):
        provider = GeminiProvider()
        
        # Test 429 rate limit mapping
        err = provider.handle_errors(Exception("429 resource_exhausted limit reached"))
        assert isinstance(err, RateLimitError)

        # Test 503 unavailable mapping
        err = provider.handle_errors(Exception("503 unavailable service overloaded"))
        assert isinstance(err, RetryableError)


# ── 5. LLMService Resilient Fallback Tests ───────────────────────────────────

class TestLLMServiceResilientFallback:
    @pytest.mark.asyncio
    async def test_llm_service_falls_back_on_503(self):
        service = LLMService()
        
        # Setup mocks
        mock_router = MagicMock()
        
        mock_gemini = MagicMock()
        mock_gemini.name = "gemini"
        mock_gemini.generate_with_tools = MagicMock(side_effect=RetryableError("Google 503 overloaded"))
        
        from unittest.mock import AsyncMock
        mock_groq = MagicMock()
        mock_groq.name = "groq"
        mock_groq.generate_with_tools = AsyncMock(return_value=ProviderResponse(
            content="Fallback successful",
            tool_calls=[]
        ))

        # Force ModelRouter to return gemini first, then groq
        mock_router.get_provider_for_task.side_effect = [mock_gemini, mock_groq]

        with patch("backend.ai.services.get_model_router", return_value=mock_router):
            content, tool_calls = await service.generate_response(
                messages=[{"role": "user", "content": "hi"}],
                system_prompt="system"
            )
            
            # Verifications
            assert content == "Fallback successful"
            assert tool_calls == []
            # Verify router marked Gemini unhealthy
            mock_router.mark_unhealthy.assert_called_once_with("gemini", cooldown_seconds=60.0)
