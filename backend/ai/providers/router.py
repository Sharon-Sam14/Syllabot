"""
backend/ai/providers/router.py

ModelRouter — intelligently routes AI tasks to the appropriate provider based on task mapping and provider health.
Tracks dynamic runtime provider health and automatically routes requests to fallbacks during cooldown periods.
"""
import time
import logging
from functools import lru_cache
from typing import Optional

from backend.ai.providers.base import (
    AIProvider,
    AllProvidersUnavailableError,
    ProviderUnavailableError,
)
from backend.ai.providers.gemini import GeminiProvider
from backend.ai.providers.groq import GroqProvider

logger = logging.getLogger("syllabot.ai.providers.router")


# ── Task → Provider mapping ───────────────────────────────────────────────────
# Defines which provider is preferred for each LangGraph node task.
TASK_PROVIDER_MAP: dict[str, str] = {
    # Gemini: semantic reasoning, large-context understanding
    "parse_syllabus":       "gemini",
    "analyze_topics":       "gemini",
    "estimate_difficulty":  "gemini",
    "general_chat":         "gemini",
    "route_intent":         "gemini",

    # Groq: speed-sensitive, structured output
    "generate_plan":        "groq",
    "generate_quiz":        "groq",
    "summarize":            "groq",
    "replan":               "groq",
    "check_progress":       "groq",
}

# Default provider if task is not found in the map
DEFAULT_PROVIDER = "gemini"


class ModelRouter:
    """
    Routes AI tasks to the best available provider.
    Maintains a thread-safe health cache with cooldown timers to handle transient failures.
    """

    def __init__(self):
        self._gemini = GeminiProvider()
        self._groq = GroqProvider()
        # Health cache schema: {provider_name: {"healthy": bool, "cooldown_until": float}}
        self._health_cache = {
            "gemini": {"healthy": True, "cooldown_until": 0.0},
            "groq": {"healthy": True, "cooldown_until": 0.0}
        }

        available = []
        if self._gemini.is_available():
            available.append("gemini")
        if self._groq.is_available():
            available.append("groq")

        logger.info(
            "ModelRouter initialized",
            extra={"available_providers": available}
        )

    def mark_unhealthy(self, provider_name: str, cooldown_seconds: float = 60.0) -> None:
        """Mark a provider as unhealthy and set a cooldown timer."""
        if not hasattr(self, "_health_cache"):
            self._health_cache = {
                "gemini": {"healthy": True, "cooldown_until": 0.0},
                "groq": {"healthy": True, "cooldown_until": 0.0}
            }
        if provider_name not in self._health_cache:
            return
        self._health_cache[provider_name] = {
            "healthy": False,
            "cooldown_until": time.time() + cooldown_seconds
        }
        logger.warning(
            f"Provider {provider_name} marked UNHEALTHY. "
            f"Cooldown active for {cooldown_seconds} seconds."
        )

    def is_healthy(self, provider_name: str) -> bool:
        """Check if a provider is currently healthy or if its cooldown has expired."""
        if not hasattr(self, "_health_cache"):
            self._health_cache = {
                "gemini": {"healthy": True, "cooldown_until": 0.0},
                "groq": {"healthy": True, "cooldown_until": 0.0}
            }
        cache = self._health_cache.get(provider_name, {"healthy": True, "cooldown_until": 0.0})
        if not cache["healthy"]:
            if time.time() >= cache["cooldown_until"]:
                # Cooldown expired, restore health
                cache["healthy"] = True
                cache["cooldown_until"] = 0.0
                logger.info(f"Provider {provider_name} cooldown expired. Restored to HEALTHY.")
        return cache["healthy"]

    def any_available(self) -> bool:
        """True if at least one provider is configured and available."""
        return self._gemini.is_available() or self._groq.is_available()

    def get_provider_for_task(self, task: str) -> AIProvider:
        """
        Return the best available provider for the given task.
        If the preferred provider is unavailable or unhealthy, falls back to the other one.
        """
        if not self.any_available():
            raise AllProvidersUnavailableError("No API keys are configured in your environment.")

        preferred_name = TASK_PROVIDER_MAP.get(task, DEFAULT_PROVIDER)
        preferred = self._gemini if preferred_name == "gemini" else self._groq
        fallback = self._groq if preferred_name == "gemini" else self._gemini

        # Case 1: Preferred is available and healthy
        if preferred.is_available() and self.is_healthy(preferred.name):
            logger.debug(
                "Router selected preferred provider",
                extra={"task": task, "provider": preferred.name}
            )
            return preferred

        # Case 2: Preferred is unavailable/unhealthy, try fallback if healthy
        if fallback.is_available() and self.is_healthy(fallback.name):
            logger.warning(
                f"Preferred provider {preferred.name} is unhealthy or unavailable. "
                f"Routing task {task} to fallback provider {fallback.name}."
            )
            return fallback

        # Case 3: Both are unhealthy, but if one is at least configured, try it as a last-resort best-effort
        if preferred.is_available():
            logger.warning(
                f"Both providers are unhealthy/unavailable. "
                f"Attempting preferred provider {preferred.name} as last-resort."
            )
            return preferred
        if fallback.is_available():
            logger.warning(
                f"Both providers are unhealthy/unavailable. "
                f"Attempting fallback provider {fallback.name} as last-resort."
            )
            return fallback

        raise AllProvidersUnavailableError("No configured providers are available to serve requests.")

    def get_gemini(self) -> GeminiProvider:
        """Direct access to Gemini provider (raises if unavailable)."""
        if not self._gemini.is_available():
            raise ProviderUnavailableError("Gemini is not configured. Set GEMINI_API_KEY in .env")
        return self._gemini

    def get_groq(self) -> GroqProvider:
        """Direct access to Groq provider (raises if unavailable)."""
        if not self._groq.is_available():
            raise ProviderUnavailableError("Groq is not configured. Set GROQ_API_KEY in .env")
        return self._groq

    def status(self) -> dict:
        """Return status summary for all providers, including health information."""
        return {
            "gemini": {
                "available": self._gemini.is_available(),
                "healthy": self.is_healthy("gemini"),
                "default_model": GeminiProvider.DEFAULT_MODEL,
            },
            "groq": {
                "available": self._groq.is_available(),
                "healthy": self.is_healthy("groq"),
                "default_model": GroqProvider.DEFAULT_MODEL,
            },
            "any_available": self.any_available(),
        }


# ── Singleton factory ─────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_model_router() -> ModelRouter:
    """Return the singleton ModelRouter instance."""
    return ModelRouter()
