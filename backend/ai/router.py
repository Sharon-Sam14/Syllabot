import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.api.v1.dependencies import get_current_user
from backend.models.user import User
from backend.ai.schemas import AIChatRequest, AIChatResponse
from backend.ai.agent import SyllabotAgent

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse, status_code=status.HTTP_200_OK)
async def ai_chat(
    chat_in: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIChatResponse:
    """
    Orchestrate the AI Agent to answer queries or perform actions based on natural language input.
    """
    # Use provided conversation_id or generate a new one
    conversation_id = chat_in.conversation_id or uuid.uuid4().hex

    try:
        agent = SyllabotAgent(db, current_user)
        response_text, actions, sources = await agent.execute(chat_in.message, conversation_id)
        
        return AIChatResponse(
            response=response_text,
            actions=actions,
            sources=sources
        )
    except Exception as e:
        # Wrap custom LLM Service exception or general exceptions into a clean HTTP 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent execution failed: {str(e)}"
        )
