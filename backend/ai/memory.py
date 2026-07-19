from typing import Any, Dict, List, Optional
import time


class BaseMemory:
    """
    Abstract base class/interface for memory managers.
    """
    async def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        raise NotImplementedError

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        raise NotImplementedError

    async def get_context(self, conversation_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def update_context(self, conversation_id: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def clear_memory(self, conversation_id: str) -> None:
        raise NotImplementedError


class InMemoryMemory(BaseMemory):
    """
    Lightweight, thread-safe in-memory memory manager implementation.
    """
    def __init__(self, max_history_len: int = 20):
        # Maps conversation_id -> { "history": [...], "context": {...}, "last_accessed": float }
        self._store: Dict[str, Dict[str, Any]] = {}
        self.max_history_len = max_history_len

    def _ensure_session(self, conversation_id: str) -> None:
        if conversation_id not in self._store:
            self._store[conversation_id] = {
                "history": [],
                "context": {},
                "last_accessed": time.time()
            }
        else:
            self._store[conversation_id]["last_accessed"] = time.time()

    async def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        self._ensure_session(conversation_id)
        return self._store[conversation_id]["history"]

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        self._ensure_session(conversation_id)
        history = self._store[conversation_id]["history"]
        history.append({"role": role, "content": content})
        # Limit history length to prevent context window bloat
        if len(history) > self.max_history_len:
            self._store[conversation_id]["history"] = history[-self.max_history_len:]

    async def get_context(self, conversation_id: str) -> Dict[str, Any]:
        self._ensure_session(conversation_id)
        return self._store[conversation_id]["context"]

    async def update_context(self, conversation_id: str, data: Dict[str, Any]) -> None:
        self._ensure_session(conversation_id)
        self._store[conversation_id]["context"].update(data)

    async def clear_memory(self, conversation_id: str) -> None:
        if conversation_id in self._store:
            del self._store[conversation_id]


# Global singleton instance of memory
memory_manager = InMemoryMemory()
