"""
backend/ai/services.py

Unified LLM Client Service.
Refactored to eliminate duplicate request pipelines.
Delegates all formatting, routing, exception mapping, and API executions
to the compiled ModelRouter and ProviderAdapter layers.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.ai.config import ai_settings
from backend.ai.prompts import TOOLS_DECLARATIONS
from backend.ai.providers.base import (
    AIException,
    RateLimitError,
    QuotaExceededError,
    RetryableError,
)
from backend.ai.providers.router import get_model_router
from backend.core.serializer import ConversationNormalizer

logger = logging.getLogger("syllabot.ai.services")


class LLMServiceException(AIException):
    """Raised when the LLM service fails to complete the transaction."""
    pass


class LLMService:
    """
    Unified client gateway for AI requests.
    Interfaces with the ModelRouter to execute requests with transparent failovers.
    """

    def __init__(self):
        # Read default provider from settings (gemini, groq)
        self.provider = ai_settings.AI_PROVIDER.lower()

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: List[Dict[str, Any]] = TOOLS_DECLARATIONS
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Send messages to the active LLM provider.
        Returns a tuple: (content_text, list_of_tool_calls)
        Handles transient/quota errors by switching providers and triggering the health cache.
        """
        try:
            # 1. Normalize list of messages using unified Message schema converter
            normalized = ConversationNormalizer.normalize(messages)
        except Exception as e:
            logger.error(f"Message normalization failed: {e}")
            raise LLMServiceException(f"Serialization error: {e}")

        router = get_model_router()
        task_key = "general_chat"

        # 2. Retrieve the active provider for the task
        try:
            provider = router.get_provider_for_task(task_key)
        except Exception as e:
            logger.error(f"No healthy provider found for task {task_key}: {e}")
            raise LLMServiceException(f"Provider routing failure: {e}")

        providers_attempted = set()
        last_error = None

        # 3. Attempt execution with active provider and fallback on transient errors
        while provider and provider.name not in providers_attempted:
            provider_name = provider.name
            providers_attempted.add(provider_name)
            logger.info(f"LLMService executing call using provider adapter: {provider_name}")

            try:
                # Execute tool-binding completion call
                response = await provider.generate_with_tools(
                    messages=normalized,
                    tools=tools,
                    system_prompt=system_prompt,
                    temperature=0.1
                )

                # Format tool calls back to legacy structure expected by the orchestrator
                tool_calls_dict = [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments
                    }
                    for tc in response.tool_calls
                ]
                return response.content, tool_calls_dict

            except (RateLimitError, QuotaExceededError, RetryableError) as e:
                logger.warning(
                    f"LLM Provider {provider_name} failed with transient/quota error: {e}. "
                    "Marking unhealthy and attempting fallback routing."
                )
                # Put provider on a 60 seconds cooldown
                router.mark_unhealthy(provider_name, cooldown_seconds=60.0)
                last_error = e

                # Re-query the router to resolve the fallback provider
                try:
                    provider = router.get_provider_for_task(task_key)
                except Exception as route_err:
                    logger.error(f"Fallback routing failed: {route_err}")
                    provider = None

            except Exception as e:
                # Unretryable errors (ValidationError, AuthenticationError) propagate immediately
                logger.error(f"LLM Provider {provider_name} failed with unretryable error: {e}")
                raise LLMServiceException(f"LLM API Error: {e}")

        raise LLMServiceException(
            f"All configured providers failed to execute the request. Last error: {last_error}"
        )
