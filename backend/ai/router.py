"""
backend/ai/router.py

FastAPI router for the Syllabot AI chat endpoint.

Security:
  - Input sanitization applied before passing to the agent.
  - AllProvidersUnavailableError returns HTTP 503 with a helpful message.
  - All other exceptions return HTTP 500.
"""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.sanitizer import sanitize_input
from backend.api.v1.dependencies import get_current_user
from backend.models.user import User
from backend.ai.schemas import AIChatRequest, AIChatResponse
from backend.ai.agent import SyllabotAgent
from backend.ai.providers.base import AllProvidersUnavailableError

logger = logging.getLogger("syllabot.ai.router")
router = APIRouter()


@router.post("/chat", response_model=AIChatResponse, status_code=status.HTTP_200_OK)
async def ai_chat(
    request: Request,
    chat_in: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIChatResponse:
    """
    Send a message to the Syllabot AI agent.

    The agent uses LangGraph to route the request to the appropriate
    AI node (parse, plan, replan, quiz, summarize, or general chat).

    Returns:
        AIChatResponse with the agent's response, executed actions, and data sources.
    """
    conversation_id = chat_in.conversation_id or uuid.uuid4().hex

    # Sanitize input before processing
    clean_message = sanitize_input(chat_in.message)
    if not clean_message:
        return AIChatResponse(
            response="Please enter a message.",
            actions=[],
            sources=[]
        )

    logger.info(
        "AI chat request",
        extra={
            "user_id": current_user.id,
            "conversation_id": conversation_id,
            "message_length": len(clean_message),
        }
    )

    try:
        agent = SyllabotAgent(db, current_user)
        response_text, actions, sources = await agent.execute(clean_message, conversation_id)

        logger.info(
            "AI chat response",
            extra={
                "user_id": current_user.id,
                "conversation_id": conversation_id,
                "tool_calls": len(actions),
            }
        )

        return AIChatResponse(
            response=response_text,
            actions=actions,
            sources=sources
        )

    except AllProvidersUnavailableError as e:
        # No API keys configured — friendly 503
        logger.warning("AI providers unavailable", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI features are not yet configured. "
                "Please add GEMINI_API_KEY or GROQ_API_KEY to your .env file. "
                "See .env.example for setup instructions."
            )
        )

    except Exception as e:
        logger.error(
            "AI agent execution failed",
            extra={"user_id": current_user.id, "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent execution failed: {str(e)}"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def ai_status(
    current_user: User = Depends(get_current_user),
):
    """
    Return the availability status of all AI providers.
    Useful for the frontend to check if AI features are available.
    """
    try:
        from backend.ai.providers.router import get_model_router
        return get_model_router().status()
    except Exception as e:
        return {"any_available": False, "error": str(e)}
