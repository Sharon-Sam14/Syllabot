"""
backend/ai/graph/state.py

AgentState — the shared state object that flows through the LangGraph workflow.

Every node receives the current state and returns an updated state dict.
LangGraph merges the returned dict with the existing state automatically.

Design principles:
  - All fields are Optional — nodes only populate what they produce.
  - 'messages' holds the full conversation history (user + assistant turns).
  - 'intent' is set by route_intent and read by conditional edges to route the graph.
  - 'final_response' is the output produced by the terminal node.
  - 'error' captures any node-level errors for graceful degradation.
"""
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state object for the Syllabot LangGraph workflow.

    Fields:
        messages:         Full conversation history in role/content format.
        system_prompt:    System instructions injected at graph entry.
        user_id:          ID of the authenticated user (set at graph entry).
        plan_id:          Active study plan ID (resolved from context).
        syllabus_id:      Active syllabus ID (resolved from context).
        intent:           Detected user intent — controls graph routing.
                          Possible values: 'parse', 'plan', 'progress',
                          'replan', 'quiz', 'summarize', 'chat'
        tool_results:     Accumulated results from tool executions.
        final_response:   The natural language response to return to the user.
        executed_actions: Log of tool calls and their outputs (for the API response).
        sources:          Data sources referenced (e.g., 'Syllabus #1').
        error:            Error message if a node fails (enables graceful degradation).
        provider_used:    Name of the AI provider that handled the request.
    """
    messages: List[Dict[str, Any]]
    system_prompt: str
    user_id: int
    plan_id: Optional[int]
    syllabus_id: Optional[int]
    intent: str
    tool_results: List[Dict[str, Any]]
    final_response: str
    executed_actions: List[Dict[str, Any]]
    sources: List[str]
    error: Optional[str]
    provider_used: str
