import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabi.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    plan_json = Column(JSON, nullable=False)  # Stores the actual schedule of days/tasks
    status = Column(String, default="active", nullable=False)  # active, completed, paused, archived
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )

    # Relationships
    syllabus = relationship("Syllabus", back_populates="plans")
    progress_records = relationship("DailyProgress", back_populates="plan", cascade="all, delete-orphan")
