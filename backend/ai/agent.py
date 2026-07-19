import json
import logging
from datetime import date
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.plan import StudyPlan
from backend.models.syllabus import Syllabus
from backend.ai.services import LLMService
from backend.ai.memory import memory_manager
from backend.ai.tools import SyllabotTools
from backend.ai.prompts import SYSTEM_PROMPT

logger = logging.getLogger("syllabot.ai.agent")


class SyllabotAgent:
    """
    Syllabot Intelligent Orchestrator.
    Manages state, invokes the LLM, executes selected tools,
    and returns a natural language response.
    """

    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self.llm_service = LLMService()
        self.tools = SyllabotTools(db, current_user)

    async def execute(self, message: str, conversation_id: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Executes the agent loop:
        1. Retrieve chat history & context.
        2. Set up context and system prompt.
        3. Invoke LLM and process tool calls iteratively.
        4. Return final response text, executed actions, and sources.
        """
        # 1. Retrieve history and active context
        history = await memory_manager.get_history(conversation_id)
        context = await memory_manager.get_context(conversation_id)

        # Proactively load default syllabus/plan into context if not present
        if "syllabus_id" not in context or "plan_id" not in context:
            await self._bootstrap_context(context, conversation_id)

        # 2. Build system prompt with current date and context information
        today_str = date.today().isoformat()
        context_notes = f"\nActive Syllabus ID: {context.get('syllabus_id', 'None')}"
        context_notes += f"\nActive Study Plan ID: {context.get('plan_id', 'None')}"
        
        system_prompt = SYSTEM_PROMPT.format(current_date=today_str) + context_notes

        # 3. Construct temporary execution message chain
        temp_messages = []
        for msg in history:
            temp_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add new user message
        temp_messages.append({"role": "user", "content": message})

        executed_actions = []
        sources = []

        # 4. Agent loop (max 5 turns to prevent infinite execution)
        max_turns = 5
        final_text = None

        for turn in range(max_turns):
            logger.info(f"Agent turn {turn + 1}/{max_turns} for conversation {conversation_id}")
            
            content, tool_calls = await self.llm_service.generate_response(
                messages=temp_messages,
                system_prompt=system_prompt
            )

            # If there are no tool calls, the LLM has formulated a final response
            if not tool_calls:
                final_text = content or "I apologize, but I could not formulate a response. Please let me know how I can help."
                break

            # Process tool calls
            # We append the assistant's request for tool execution to the temp messages
            assistant_tool_msg = {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            }
            temp_messages.append(assistant_tool_msg)

            for tc in tool_calls:
                tc_id = tc["id"]
                tc_name = tc["name"]
                tc_args = tc["arguments"]

                logger.info(f"Agent executing tool: {tc_name} with args: {tc_args}")
                
                # Retrieve the tool method dynamically
                tool_method = getattr(self.tools, tc_name, None)
                if tool_method:
                    try:
                        # Extract and call the tool
                        result = tool_method(**tc_args)
                        result_str = json.dumps(result)
                        
                        # Add to executed actions log
                        executed_actions.append({
                            "tool": tc_name,
                            "arguments": tc_args,
                            "output": result
                        })

                        # Track data sources if applicable
                        if "syllabus_id" in tc_args:
                            sources.append(f"Syllabus #{tc_args['syllabus_id']}")
                        if "plan_id" in tc_args:
                            sources.append(f"Study Plan #{tc_args['plan_id']}")

                        # Update memory context if a new plan or syllabus was created/referenced
                        if tc_name == "generate_plan" and "plan_id" in result:
                            context["plan_id"] = result["plan_id"]
                            context["syllabus_id"] = result["syllabus_id"]
                            await memory_manager.update_context(conversation_id, context)
                        elif tc_name == "get_topics" and "syllabus_id" in result:
                            context["syllabus_id"] = result["syllabus_id"]
                            await memory_manager.update_context(conversation_id, context)

                    except Exception as e:
                        logger.error(f"Error executing tool {tc_name}: {str(e)}")
                        result_str = json.dumps({"error": f"Tool execution failed: {str(e)}"})
                else:
                    result_str = json.dumps({"error": f"Tool '{tc_name}' is not registered."})

                # Append the tool result back to temp_messages
                temp_messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "name": tc_name,
                    "content": result_str
                })

        # Save final state to memory history
        if final_text:
            await memory_manager.add_message(conversation_id, "user", message)
            await memory_manager.add_message(conversation_id, "assistant", final_text)
        else:
            final_text = "I encountered an error while trying to complete your request. Please try again."

        return final_text, executed_actions, list(set(sources))

    async def _bootstrap_context(self, context: Dict[str, Any], conversation_id: str) -> None:
        """
        Helper to dynamically load default/latest syllabus and plan IDs into the memory context.
        """
        # Find latest active study plan
        latest_plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(Syllabus.user_id == self.current_user.id)
            .order_by(StudyPlan.id.desc())
            .first()
        )
        if latest_plan:
            context["plan_id"] = latest_plan.id
            context["syllabus_id"] = latest_plan.syllabus_id
            await memory_manager.update_context(conversation_id, context)
            return

        # Fallback to latest syllabus if no plan exists
        latest_syllabus = (
            self.db.query(Syllabus)
            .filter(Syllabus.user_id == self.current_user.id)
            .order_by(Syllabus.id.desc())
            .first()
        )
        if latest_syllabus:
            context["syllabus_id"] = latest_syllabus.id
            await memory_manager.update_context(conversation_id, context)
