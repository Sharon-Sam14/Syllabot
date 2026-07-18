from datetime import date
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class DailyProgressBase(BaseModel):
    date: date
    completed_hours: float = 0.0
    completed_topics: Optional[Any] = None
    check_in_note: Optional[str] = None


class DailyProgressCreate(DailyProgressBase):
    pass


class DailyProgressResponse(DailyProgressBase):
    id: int
    plan_id: int

    model_config = ConfigDict(from_attributes=True)
