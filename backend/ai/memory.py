"""
backend/ai/memory.py

Memory management for the Syllabot AI agent.

Two memory implementations:

1. InMemoryMemory (default, singleton)
   - Stores conversation history (messages) and short-lived context (plan_id, syllabus_id)
   - Fast, zero-latency reads/writes
   - Resets on server restart by design (conversations are ephemeral)
   - Used by: SyllabotAgent for all conversation history

2. DatabaseMemory
   - Persists user learning profiles (preferences, weak topics, strengths, streak)
   - Survives server restarts
   - Used by: LangGraph nodes that need personalized context
   - Backed by: UserMemory SQLAlchemy model
"""
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
    Stores conversation history and short-lived session context.
    Resets on server restart — this is intentional for conversation sessions.
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


class DatabaseMemory:
    """
    Persistent memory backed by the UserMemory SQLAlchemy model.

    Reads and writes user learning profiles that survive server restarts.
    Used by LangGraph nodes to personalize AI responses based on the
    student's accumulated learning history.

    Usage:
        db_memory = DatabaseMemory(db_session)
        profile = await db_memory.get_user_profile(user_id)
        await db_memory.update_weak_topics(user_id, weak_topic_ids)
    """

    def __init__(self, db):
        """
        Args:
            db: SQLAlchemy Session instance.
        """
        self._db = db

    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the persistent memory profile for a user.
        Returns None if no profile exists yet.
        """
        try:
            from backend.models.user_memory import UserMemory
            record = self._db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
            if record:
                return record.to_context_dict()
            return None
        except Exception:
            return None

    async def get_or_create_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve the user's memory profile, creating an empty one if it doesn't exist.
        """
        try:
            from backend.models.user_memory import UserMemory
            import datetime

            record = self._db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
            if not record:
                record = UserMemory(
                    user_id=user_id,
                    preferences={},
                    weak_topics=[],
                    strengths=[],
                    streak_days=0,
                )
                self._db.add(record)
                self._db.commit()
                self._db.refresh(record)

            record.update_last_active()
            self._db.commit()
            return record.to_context_dict()
        except Exception:
            return {"preferences": {}, "weak_topics": [], "strengths": [], "streak_days": 0}

    async def update_preferences(self, user_id: int, preferences: Dict[str, Any]) -> None:
        """Update study preferences for a user (merges with existing)."""
        try:
            from backend.models.user_memory import UserMemory
            record = self._db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
            if record:
                existing = dict(record.preferences or {})
                existing.update(preferences)
                record.preferences = existing
                self._db.commit()
        except Exception:
            pass

    async def update_weak_topics(self, user_id: int, weak_topic_ids: List[str]) -> None:
        """Record topics the student is struggling with."""
        try:
            from backend.models.user_memory import UserMemory
            record = self._db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
            if record:
                existing_ids = {t.get("id") for t in (record.weak_topics or [])}
                for topic_id in weak_topic_ids:
                    if topic_id not in existing_ids:
                        weak = list(record.weak_topics or [])
                        weak.append({"id": topic_id, "miss_count": 1})
                        record.weak_topics = weak
                self._db.commit()
        except Exception:
            pass

    async def increment_streak(self, user_id: int) -> int:
        """
        Increment the study streak for a user.
        Returns the new streak count.
        """
        try:
            from backend.models.user_memory import UserMemory
            record = self._db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
            if record:
                record.streak_days = (record.streak_days or 0) + 1
                if record.streak_days > (record.longest_streak or 0):
                    record.longest_streak = record.streak_days
                record.update_last_active()
                self._db.commit()
                return record.streak_days
            return 0
        except Exception:
            return 0


# Global singleton instance for conversation history (short-lived, in-memory)
memory_manager = InMemoryMemory()
