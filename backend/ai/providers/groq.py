"""
backend/ai/providers/groq.py

GroqProvider Adapter.
Consumes unified Message structures, translates them to LangChain Groq formats,
handles API call execution, and wraps Groq status responses in classified typed exceptions.
"""
import time
import logging
from typing import Any, Dict, List, Optional

from backend.ai.providers.base import (
    AIProvider,
    Message,
    ToolCall,
    ProviderResponse,
    ProviderError,
    RetryableError,
    QuotaExceededError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    ProviderUnavailableError,
)
from backend.core.config import settings

logger = logging.getLogger("syllabot.ai.providers.groq")


class GroqProvider(AIProvider):
    """
    Adapter for Groq Cloud using langchain-groq.
    """

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    @property
    def name(self) -> str:
        return "groq"

    def is_available(self) -> bool:
        """True if GROQ_API_KEY is configured in the environment."""
        return bool(settings.GROQ_API_KEY)

    def _require_available(self) -> None:
        if not self.is_available():
            raise ProviderUnavailableError(
                "Groq provider is not configured. Set GROQ_API_KEY in .env."
            )

    def _get_model_name(self) -> str:
        return settings.AI_MODEL or self.DEFAULT_MODEL

    # ── Adapter Implementations ───────────────────────────────────────────────

    def prepare_messages(self, messages: List[Message], system_prompt: Optional[str]) -> list:
        """
        Convert unified Message objects into LangChain message schemas.
        Ensures correct mapping of tool call IDs for OpenAI spec compatibility.
        """
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

        lc_messages = []
        if system_prompt:
            lc_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            role = msg.role
            content = msg.content or ""

            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                if msg.tool_calls:
                    lc_tool_calls = [
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "args": tc.arguments,
                            "type": "tool_call"
                        }
                        for tc in msg.tool_calls
                    ]
                    lc_messages.append(AIMessage(content=content, tool_calls=lc_tool_calls))
                else:
                    lc_messages.append(AIMessage(content=content))
            elif role == "tool":
                tool_id = msg.tool_call_id or "mock_tool_id"
                lc_messages.append(ToolMessage(content=content, tool_call_id=tool_id))
            else:
                logger.warning(f"Skipping unknown message role during Groq serialization: {role}")

        return lc_messages

    async def execute(
        self,
        payload: Any,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Any:
        """Call the LangChain ChatGroq executor."""
        from langchain_groq import ChatGroq

        model_name = self._get_model_name()
        llm = ChatGroq(
            model=model_name,
            api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if tools and self.supports_tools():
            # Translate unified tool definitions to OpenAI-compatible tools format
            groq_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("parameters", {}),
                    }
                }
                for t in tools
            ]
            if groq_tools:
                llm = llm.bind_tools(groq_tools)

        logger.info(
            "Groq generate content request",
            extra={"model": model_name, "message_count": len(payload)}
        )

        return await llm.ainvoke(payload)

    def parse_response(self, raw_response: Any) -> ProviderResponse:
        """Translate LangChain response object to unified ProviderResponse."""
        content = raw_response.content if isinstance(raw_response.content, str) else None
        
        tool_calls = []
        if hasattr(raw_response, "tool_calls") and raw_response.tool_calls:
            for tc in raw_response.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.get("id", f"groq_{tc['name']}"),
                    name=tc["name"],
                    arguments=tc.get("args", {})
                ))

        model_name = self._get_model_name()
        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            model=model_name
        )

    def handle_errors(self, exception: Exception) -> Exception:
        """Classify Groq API exceptions into typed errors."""
        err_msg = str(exception).lower()

        # Quota and rate limiting errors
        if "quota exceeded" in err_msg or "quota_exceeded" in err_msg:
            return QuotaExceededError(f"Groq API quota exceeded: {exception}")
        if "429" in err_msg or "rate limit" in err_msg or "rate_limit_exceeded" in err_msg:
            return RateLimitError(f"Groq API rate limited: {exception}")

        # Transient connection/overload failures
        if "503" in err_msg or "unavailable" in err_msg or "service_unavailable" in err_msg:
            return RetryableError(f"Groq API temporarily unavailable: {exception}")

        # Authentication errors
        if "401" in err_msg or "403" in err_msg or "api key not valid" in err_msg or "invalid api key" in err_msg:
            return AuthenticationError(f"Groq API authentication failed: {exception}")

        # Schema or tool validation failures
        if "400" in err_msg or "validation" in err_msg or "bad request" in err_msg or "tool_use_failed" in err_msg:
            return ValidationError(f"Groq API parameter validation failed: {exception}")

        return ProviderError(f"Groq API call failed: {exception}")

    # ── Capabilities ──────────────────────────────────────────────────────────

    def supports_tools(self) -> bool:
        return True

    def supports_images(self) -> bool:
        return False

    def supports_streaming(self) -> bool:
        return True
