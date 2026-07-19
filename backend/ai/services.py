import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple
import httpx

from backend.ai.config import ai_settings
from backend.ai.prompts import SYSTEM_PROMPT, TOOLS_DECLARATIONS

logger = logging.getLogger("syllabot.ai.services")


class LLMServiceException(Exception):
    pass


class LLMService:
    """
    Unified client for OpenAI, Gemini, Groq, and Claude.
    Handles payloads, API calls, tool schema translation, and retry logic.
    """

    def __init__(self):
        self.provider = ai_settings.AI_PROVIDER.lower()
        self.api_key = None
        self.model = None

    def _get_api_key(self) -> str:
        if self.provider == "openai":
            key = ai_settings.OPENAI_API_KEY
        elif self.provider == "gemini":
            key = ai_settings.GEMINI_API_KEY
        elif self.provider == "groq":
            key = ai_settings.GROQ_API_KEY
        elif self.provider == "claude":
            key = ai_settings.CLAUDE_API_KEY
        else:
            raise LLMServiceException(f"Unsupported AI provider: {self.provider}")

        if not key:
            raise LLMServiceException(f"API Key for provider '{self.provider}' is not configured.")
        return key

    def _get_model(self) -> str:
        if ai_settings.AI_MODEL:
            return ai_settings.AI_MODEL

        # Fallback defaults
        defaults = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-1.5-flash",
            "groq": "llama3-8b-8192",
            "claude": "claude-3-5-sonnet-20240620"
        }
        return defaults.get(self.provider, "gpt-4o-mini")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]] = TOOLS_DECLARATIONS
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Send messages to the active LLM provider.
        Returns a tuple: (content_text, list_of_tool_calls)
        Each tool call is formatted as: {"id": str, "name": str, "arguments": dict}
        """
        # Lazy load/validate at runtime to support mocking and key-less init
        self.api_key = self._get_api_key()
        self.model = self._get_model()

        # Execute with retry logic (up to 3 times)
        max_retries = 3
        backoff_seconds = 1

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if self.provider == "openai":
                        return await self._call_openai(client, messages, system_prompt, tools)
                    elif self.provider == "groq":
                        return await self._call_groq(client, messages, system_prompt, tools)
                    elif self.provider == "gemini":
                        return await self._call_gemini(client, messages, system_prompt, tools)
                    elif self.provider == "claude":
                        return await self._call_claude(client, messages, system_prompt, tools)
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"HTTP error from LLM provider (attempt {attempt + 1}/{max_retries}): "
                    f"{e.response.status_code} - {e.response.text}"
                )
                if e.response.status_code == 429:
                    # Rate limiting - increase backoff
                    await asyncio.sleep(backoff_seconds * 2)
                elif e.response.status_code in (400, 401, 403, 404):
                    # Client errors (auth/config/bad payload) should not retry
                    raise LLMServiceException(f"LLM API Error: {e.response.text}")
            except Exception as e:
                logger.warning(f"Connection error to LLM (attempt {attempt + 1}/{max_retries}): {str(e)}")

            if attempt < max_retries - 1:
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2
            else:
                raise LLMServiceException("Failed to communicate with LLM provider after multiple retries.")

        return None, []

    # --- OpenAI ---
    async def _call_openai(
        self,
        client: httpx.AsyncClient,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build messages payload
        payload_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            payload_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "tools": [{"type": "function", "function": t} for t in tools],
            "tool_choice": "auto"
        }

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()

        message = res_data["choices"][0]["message"]
        content = message.get("content")
        tool_calls = []

        for tc in message.get("tool_calls", []):
            if tc.get("type") == "function":
                func = tc["function"]
                try:
                    args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append({
                    "id": tc["id"],
                    "name": func["name"],
                    "arguments": args
                })

        return content, tool_calls

    # --- Groq ---
    async def _call_groq(
        self,
        client: httpx.AsyncClient,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            payload_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "tools": [{"type": "function", "function": t} for t in tools],
            "tool_choice": "auto"
        }

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()

        message = res_data["choices"][0]["message"]
        content = message.get("content")
        tool_calls = []

        for tc in message.get("tool_calls", []):
            if tc.get("type") == "function":
                func = tc["function"]
                try:
                    args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append({
                    "id": tc["id"],
                    "name": func["name"],
                    "arguments": args
                })

        return content, tool_calls

    # --- Claude / Anthropic ---
    async def _call_claude(
        self,
        client: httpx.AsyncClient,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Anthropic doesn't allow 'system' inside message list; it is passed as root property
        payload_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "assistant":
                role = "assistant"
            elif role == "user":
                role = "user"
            else:
                continue
            payload_messages.append({"role": role, "content": msg["content"]})

        # Translate tools to Anthropic format
        claude_tools = []
        for t in tools:
            claude_tools.append({
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"]
            })

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": payload_messages,
            "tools": claude_tools,
            "max_tokens": 1024
        }

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()

        content = None
        tool_calls = []

        for part in res_data.get("content", []):
            if part.get("type") == "text":
                content = part.get("text")
            elif part.get("type") == "tool_use":
                tool_calls.append({
                    "id": part["id"],
                    "name": part["name"],
                    "arguments": part["input"]
                })

        return content, tool_calls

    # --- Gemini ---
    async def _call_gemini(
        self,
        client: httpx.AsyncClient,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        # Google Generative Language REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }

        # Build contents structure: Gemini roles must alternate (user/model)
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # If no messages exist or last is not user, Gemini might error, ensure we have at least one user part
        if not contents:
            contents.append({
                "role": "user",
                "parts": [{"text": "Hello"}]
            })

        # Gemini tool schemas: convert schema declarations to functionDeclarations
        gemini_tools = [
            {
                "functionDeclarations": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"]
                    }
                    for t in tools
                ]
            }
        ]

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "tools": gemini_tools
        }

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()

        content = None
        tool_calls = []

        candidates = res_data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    content = part["text"]
                elif "functionCall" in part:
                    f_call = part["functionCall"]
                    tool_calls.append({
                        # Gemini function calls don't return a transaction ID natively, so we create a mock one
                        "id": f"gemini_{f_call['name']}",
                        "name": f_call["name"],
                        "arguments": f_call.get("args", {})
                    })

        return content, tool_calls
