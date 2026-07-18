from datetime import date, datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class StudyPlanBase(BaseModel):
    start_date: date
    end_date: date
    status: str = "active"


class StudyPlanCreate(StudyPlanBase):
    syllabus_id: int


class StudyPlanResponse(StudyPlanBase):
    id: int
    syllabus_id: int
    plan_json: Any
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
