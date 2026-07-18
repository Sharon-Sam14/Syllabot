import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_tree_json = Column(JSON, nullable=True)  # Store structured hierarchy JSON
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )

    # Relationships
    user = relationship("User", back_populates="syllabi")
    plans = relationship("StudyPlan", back_populates="syllabus", cascade="all, delete-orphan")
