"""
backend/models/user_memory.py

UserMemory — persistent learning profile for each student.

Stores per-user AI memory that survives server restarts:
  - Study preferences (speed, style, daily hours)
  - Weak topics identified through progress analysis
  - Known strengths
  - Study streak tracking
  - Last active timestamp

This complements the InMemoryMemory (conversation history, short-lived)
which resets each server restart by design.

Relationship: One UserMemory record per User (one-to-one via user_id).
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


class UserMemory(Base):
    """
    Persistent AI memory profile for a student.

    The 'preferences' and other JSON fields store arbitrary structured data
    that evolves as the student uses the app. The AI reads this on each
    conversation to personalize its responses.
    """
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)

    # One-to-one with User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # ── Study preferences ──────────────────────────────────────────────
    # Example: {"daily_study_hours": 2.5, "learning_style": "visual",
    #           "preferred_session_length": 45, "study_speed": "moderate"}
    preferences: dict = Column(JSON, default=dict, nullable=False)

    # ── Weak topics (topic IDs + titles the student struggles with) ────
    # Example: [{"id": "t_001", "title": "Newton's Laws", "miss_count": 3}]
    weak_topics: list = Column(JSON, default=list, nullable=False)

    # ── Strengths (topic IDs + titles the student excels at) ──────────
    # Example: [{"id": "t_005", "title": "Kinematics", "score": 0.9}]
    strengths: list = Column(JSON, default=list, nullable=False)

    # ── Streak tracking ───────────────────────────────────────────────
    streak_days = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)

    # ── Timestamps ────────────────────────────────────────────────────
    last_active = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        nullable=True,
    )

    # ── Relationship ──────────────────────────────────────────────────
    user = relationship("User", back_populates="memory")

    def update_last_active(self) -> None:
        """Mark the student as active right now."""
        self.last_active = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    def to_context_dict(self) -> dict:
        """
        Return a summary suitable for injecting into AI system prompts.
        Used by the DatabaseMemory class to personalize AI responses.
        """
        return {
            "preferences": self.preferences or {},
            "weak_topics": [t.get("title") for t in (self.weak_topics or [])],
            "strengths": [t.get("title") for t in (self.strengths or [])],
            "streak_days": self.streak_days,
        }
