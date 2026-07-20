"""
backend/ai/graph/workflow.py

LangGraph StateGraph assembly for the Syllabot AI workflow.

This module builds and compiles the complete agent workflow graph.
The compiled graph is a singleton — created once and reused across requests.

Graph topology:
  START → route_intent → [conditional routing by intent] → [task node] → END

All task nodes are terminal (they route to END after completion).
The error_node is an optional terminal node for handling failures.
"""
import logging
from functools import lru_cache
from typing import Any

from langgraph.graph import StateGraph, START, END

from backend.ai.graph.state import AgentState
from backend.ai.graph.nodes import (
    route_intent,
    parse_node,
    plan_node,
    progress_node,
    replan_node,
    quiz_node,
    summarize_node,
    chat_node,
    error_node,
)
from backend.ai.graph.edges import route_by_intent

logger = logging.getLogger("syllabot.ai.graph.workflow")


def build_graph() -> Any:
    """
    Assemble and compile the Syllabot LangGraph StateGraph.

    Graph structure:
      START
        └─▶ route_intent (detects intent from user message)
              │
              ├─▶ parse_node     (intent: 'parse')
              ├─▶ plan_node      (intent: 'plan')
              ├─▶ progress_node  (intent: 'progress')
              ├─▶ replan_node    (intent: 'replan')
              ├─▶ quiz_node      (intent: 'quiz')
              ├─▶ summarize_node (intent: 'summarize')
              └─▶ chat_node      (intent: 'chat' / default)
                    │
                    └─▶ END (all task nodes route to END)

    Returns:
        A compiled LangGraph runnable that accepts AgentState and returns AgentState.
    """
    workflow = StateGraph(AgentState)

    # ── Register all nodes ────────────────────────────────────────────────────
    workflow.add_node("route_intent",   route_intent)
    workflow.add_node("parse_node",     parse_node)
    workflow.add_node("plan_node",      plan_node)
    workflow.add_node("progress_node",  progress_node)
    workflow.add_node("replan_node",    replan_node)
    workflow.add_node("quiz_node",      quiz_node)
    workflow.add_node("summarize_node", summarize_node)
    workflow.add_node("chat_node",      chat_node)
    workflow.add_node("error_node",     error_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    workflow.add_edge(START, "route_intent")

    # ── Conditional routing from route_intent ─────────────────────────────────
    workflow.add_conditional_edges(
        "route_intent",
        route_by_intent,
        {
            "parse_node":     "parse_node",
            "plan_node":      "plan_node",
            "progress_node":  "progress_node",
            "replan_node":    "replan_node",
            "quiz_node":      "quiz_node",
            "summarize_node": "summarize_node",
            "chat_node":      "chat_node",
        }
    )

    # ── All task nodes route to END ───────────────────────────────────────────
    for node_name in [
        "parse_node", "plan_node", "progress_node",
        "replan_node", "quiz_node", "summarize_node",
        "chat_node", "error_node",
    ]:
        workflow.add_edge(node_name, END)

    # ── Compile ───────────────────────────────────────────────────────────────
    compiled = workflow.compile()
    logger.info("Syllabot LangGraph workflow compiled successfully")
    return compiled


@lru_cache(maxsize=1)
def get_compiled_graph():
    """
    Return the singleton compiled LangGraph workflow.

    The graph is compiled once at first call and cached for the process lifetime.
    lru_cache ensures thread-safe single initialization.
    """
    return build_graph()
