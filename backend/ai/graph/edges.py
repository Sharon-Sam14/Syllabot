"""
backend/ai/graph/edges.py

Conditional edge functions for the Syllabot LangGraph workflow.

Edges read the 'intent' field set by route_intent and return the name
of the next node to execute. LangGraph uses these return values to
determine graph routing.
"""
from backend.ai.graph.state import AgentState


def route_by_intent(state: AgentState) -> str:
    """
    Conditional edge: route the graph based on the detected intent.

    Called after route_intent node. Returns the node name to execute next.

    Intent → Node mapping:
      'parse'     → parse_node     (Gemini: syllabus analysis)
      'plan'      → plan_node      (Groq: plan generation)
      'progress'  → progress_node  (Groq: progress feedback)
      'replan'    → replan_node    (Groq: adaptive replanning)
      'quiz'      → quiz_node      (Groq: quiz generation)
      'summarize' → summarize_node (Groq: topic summary)
      'chat'      → chat_node      (Gemini: general conversation)
      default     → chat_node
    """
    intent = state.get("intent", "chat")

    routing_map = {
        "parse":     "parse_node",
        "plan":      "plan_node",
        "progress":  "progress_node",
        "replan":    "replan_node",
        "quiz":      "quiz_node",
        "summarize": "summarize_node",
        "chat":      "chat_node",
    }

    return routing_map.get(intent, "chat_node")


def check_for_error(state: AgentState) -> str:
    """
    Optional edge: check if the previous node produced an error.
    Routes to error_node if an error is present, otherwise to END.
    """
    if state.get("error"):
        return "error_node"
    return "__end__"
