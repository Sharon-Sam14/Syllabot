import datetime
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.backend.core.database import Base


class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    completed_hours = Column(Float, default=0.0, nullable=False)
    completed_topics = Column(JSON, nullable=True)  # List of topic IDs or keys completed on this date
    check_in_note = Column(String, nullable=True)

    # Relationships
    plan = relationship("StudyPlan", back_populates="progress_records")
