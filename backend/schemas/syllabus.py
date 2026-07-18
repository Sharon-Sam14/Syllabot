from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class SyllabusBase(BaseModel):
    raw_text: str


class SyllabusCreate(SyllabusBase):
    pass


class SyllabusResponse(SyllabusBase):
    id: int
    user_id: int
    parsed_tree_json: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
