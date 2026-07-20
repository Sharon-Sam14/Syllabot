"""
backend/ai/providers/gemini.py

GeminiProvider Adapter.
Consumes unified Message schemas, translates them to LangChain Google GenAI formats,
handles execution, telemetry, and maps Google API status codes to classified typed exceptions.
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

logger = logging.getLogger("syllabot.ai.providers.gemini")


class GeminiProvider(AIProvider):
    """
    Adapter for Google Gemini using langchain-google-genai.
    """

    DEFAULT_MODEL = "gemini-3.5-flash"

    @property
    def name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        """True if GEMINI_API_KEY is configured in the environment."""
        return bool(settings.GEMINI_API_KEY)

    def _require_available(self) -> None:
        if not self.is_available():
            raise ProviderUnavailableError(
                "Gemini provider is not configured. Set GEMINI_API_KEY in .env."
            )

    def _get_model_name(self) -> str:
        return settings.AI_MODEL or self.DEFAULT_MODEL

    # ── Adapter Implementations ───────────────────────────────────────────────

    def prepare_messages(self, messages: List[Message], system_prompt: Optional[str]) -> list:
        """
        Convert unified Message objects into LangChain message schemas.
        Ensures correct mapping of system prompt, assistant tool calls, and tool responses.
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
                    # Translate tool call properties into LangChain format
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
                # LangChain expects ToolMessage for function outputs
                tool_id = msg.tool_call_id or "mock_tool_id"
                lc_messages.append(ToolMessage(content=content, tool_call_id=tool_id))
            else:
                logger.warning(f"Skipping unknown message role during Gemini serialization: {role}")

        return lc_messages

    async def execute(
        self,
        payload: Any,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Any:
        """Call the LangChain ChatGoogleGenerativeAI executor."""
        from langchain_google_genai import ChatGoogleGenerativeAI

        model_name = self._get_model_name()
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if tools and self.supports_tools():
            # Translate unified tool definitions to LangChain tools format
            lc_tools = self._build_langchain_tools(tools)
            if lc_tools:
                llm = llm.bind_tools(lc_tools)

        logger.info(
            "Gemini generate content request",
            extra={"model": model_name, "message_count": len(payload)}
        )

        # Execute completion call
        return await llm.ainvoke(payload)

    def parse_response(self, raw_response: Any) -> ProviderResponse:
        """Translate LangChain AIMessage response to unified ProviderResponse."""
        content = raw_response.content if isinstance(raw_response.content, str) else None
        
        tool_calls = []
        if hasattr(raw_response, "tool_calls") and raw_response.tool_calls:
            for tc in raw_response.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.get("id", f"gemini_{tc['name']}"),
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
        """Classify exceptions into typed errors (QuotaExceededError, RateLimitError, etc.)."""
        err_msg = str(exception).lower()

        # Quota and rate limiting errors
        if "quota exceeded" in err_msg or "quota_exceeded" in err_msg:
            return QuotaExceededError(f"Gemini API quota exceeded: {exception}")
        if "429" in err_msg or "rate limit" in err_msg or "resource_exhausted" in err_msg:
            return RateLimitError(f"Gemini API rate limited: {exception}")

        # Transient service errors (safe to retry)
        if "503" in err_msg or "unavailable" in err_msg or "high demand" in err_msg:
            return RetryableError(f"Gemini API temporarily unavailable: {exception}")

        # Authentication errors
        if "401" in err_msg or "403" in err_msg or "api key not valid" in err_msg or "invalid api key" in err_msg:
            return AuthenticationError(f"Gemini API authentication failed: {exception}")

        # Validation or parameter failures (do not retry)
        if "400" in err_msg or "invalid_argument" in err_msg or "bad request" in err_msg:
            return ValidationError(f"Gemini API bad request validation failed: {exception}")

        return ProviderError(f"Gemini API call failed: {exception}")

    # ── Capabilities ──────────────────────────────────────────────────────────

    def supports_tools(self) -> bool:
        return True

    def supports_images(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return True

    # ── Tool Builder Helper ───────────────────────────────────────────────────

    def _build_langchain_tools(self, tools: List[Dict[str, Any]]) -> list:
        """Convert Syllabot unified tools schema declarations into LangChain objects."""
        from langchain_core.tools import StructuredTool

        lc_tools = []
        for tool_def in tools:
            # Create a no-op callable (actual execution is done in SyllabotTools)
            def _noop(**kwargs):
                return kwargs

            lc_tool = StructuredTool.from_function(
                func=_noop,
                name=tool_def["name"],
                description=tool_def.get("description", ""),
                args_schema=None,
            )
            # Override function details using our explicit json schemas
            lc_tools.append({
                "type": "function",
                "function": {
                    "name": tool_def["name"],
                    "description": tool_def.get("description", ""),
                    "parameters": tool_def.get("parameters", {}),
                }
            })

        return lc_tools
