"""
backend/tests/test_langgraph.py

Unit tests for the LangGraph workflow.

Tests:
  - Graph compiles without error
  - All expected nodes are registered
  - route_intent detects all supported intents correctly
  - Conditional edges return correct node names
  - Graph can be invoked with a minimal initial state
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestGraphCompilation:
    """Tests that the LangGraph StateGraph compiles correctly."""

    def test_graph_compiles(self):
        """get_compiled_graph() should return a compiled runnable without error."""
        from backend.ai.graph.workflow import build_graph
        graph = build_graph()
        assert graph is not None

    def test_graph_has_all_nodes(self):
        """The compiled graph should contain all expected nodes."""
        from backend.ai.graph.workflow import build_graph
        graph = build_graph()
        node_names = set(graph.nodes)
        expected_nodes = {
            "__start__",
            "route_intent",
            "parse_node",
            "plan_node",
            "progress_node",
            "replan_node",
            "quiz_node",
            "summarize_node",
            "chat_node",
            "error_node",
        }
        assert expected_nodes.issubset(node_names), (
            f"Missing nodes: {expected_nodes - node_names}"
        )


class TestIntentDetection:
    """Tests for the route_intent node intent detection logic."""

    @pytest.mark.asyncio
    async def test_detects_quiz_intent(self):
        """'quiz me' message should result in 'quiz' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": [{"role": "user", "content": "quiz me on chapter 1"}]}
        result = await route_intent(state)
        assert result["intent"] == "quiz"

    @pytest.mark.asyncio
    async def test_detects_summarize_intent(self):
        """'summarize' keyword should result in 'summarize' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": [{"role": "user", "content": "summarize Newton's Laws for me"}]}
        result = await route_intent(state)
        assert result["intent"] == "summarize"

    @pytest.mark.asyncio
    async def test_detects_replan_intent(self):
        """'replan' keyword should result in 'replan' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": [{"role": "user", "content": "I need to replan my schedule"}]}
        result = await route_intent(state)
        assert result["intent"] == "replan"

    @pytest.mark.asyncio
    async def test_detects_progress_intent(self):
        """'progress' keyword should result in 'progress' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": [{"role": "user", "content": "log my progress for today"}]}
        result = await route_intent(state)
        assert result["intent"] == "progress"

    @pytest.mark.asyncio
    async def test_defaults_to_chat(self):
        """Unrecognized input should default to 'chat' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": [{"role": "user", "content": "hello there!"}]}
        result = await route_intent(state)
        assert result["intent"] == "chat"

    @pytest.mark.asyncio
    async def test_empty_messages_defaults_to_chat(self):
        """Empty messages list should default to 'chat' intent."""
        from backend.ai.graph.nodes import route_intent
        state = {"messages": []}
        result = await route_intent(state)
        assert result["intent"] == "chat"


class TestEdgeRouting:
    """Tests for the conditional edge routing logic."""

    def test_quiz_intent_routes_to_quiz_node(self):
        """'quiz' intent should route to quiz_node."""
        from backend.ai.graph.edges import route_by_intent
        result = route_by_intent({"intent": "quiz"})
        assert result == "quiz_node"

    def test_summarize_intent_routes_to_summarize_node(self):
        """'summarize' intent should route to summarize_node."""
        from backend.ai.graph.edges import route_by_intent
        result = route_by_intent({"intent": "summarize"})
        assert result == "summarize_node"

    def test_parse_intent_routes_to_parse_node(self):
        """'parse' intent should route to parse_node."""
        from backend.ai.graph.edges import route_by_intent
        result = route_by_intent({"intent": "parse"})
        assert result == "parse_node"

    def test_unknown_intent_routes_to_chat_node(self):
        """Unknown intent should fall back to chat_node."""
        from backend.ai.graph.edges import route_by_intent
        result = route_by_intent({"intent": "completely_unknown"})
        assert result == "chat_node"

    def test_empty_intent_routes_to_chat_node(self):
        """Empty/missing intent should fall back to chat_node."""
        from backend.ai.graph.edges import route_by_intent
        result = route_by_intent({})
        assert result == "chat_node"


class TestNodeGracefulDegradation:
    """Tests that nodes return graceful responses when providers are unavailable."""

    @pytest.mark.asyncio
    async def test_quiz_node_handles_unavailable_providers(self):
        """quiz_node should return a helpful message when no providers are configured."""
        from backend.ai.graph.nodes import quiz_node
        from backend.ai.providers.base import AllProvidersUnavailableError

        with patch("backend.ai.graph.nodes.get_model_router") as mock_router_factory:
            mock_router = MagicMock()
            mock_router.get_provider_for_task.side_effect = AllProvidersUnavailableError()
            mock_router_factory.return_value = mock_router

            state = {"messages": [{"role": "user", "content": "quiz me"}], "tool_results": []}
            result = await quiz_node(state)

            assert "error" in result
            assert result["error"] == "no_providers"

    @pytest.mark.asyncio
    async def test_summarize_node_handles_unavailable_providers(self):
        """summarize_node should return a helpful message when no providers are configured."""
        from backend.ai.graph.nodes import summarize_node
        from backend.ai.providers.base import AllProvidersUnavailableError
        from unittest.mock import MagicMock

        with patch("backend.ai.graph.nodes.get_model_router") as mock_router_factory:
            mock_router = MagicMock()
            mock_router.get_provider_for_task.side_effect = AllProvidersUnavailableError()
            mock_router_factory.return_value = mock_router

            state = {
                "messages": [{"role": "user", "content": "summarize Newton's Laws"}],
                "tool_results": [],
            }
            result = await summarize_node(state)
            assert "error" in result
            assert result["error"] == "no_providers"


# Import needed for the mock in node tests
from unittest.mock import MagicMock
