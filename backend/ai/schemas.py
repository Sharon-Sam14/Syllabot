from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str = Field(..., description="The natural language message from the user")
    conversation_id: Optional[str] = Field(None, description="Unique identifier for the chat session")


class AIChatResponse(BaseModel):
    response: str = Field(..., description="The natural language response from the AI assistant")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="List of backend actions executed by the agent")
    sources: List[str] = Field(default_factory=list, description="List of data sources or references used for the response")
