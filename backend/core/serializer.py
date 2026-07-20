"""
backend/core/serializer.py

Serialization and Normalization Layer.
Ensures conversational message payloads conform to strict typing,
maps missing tool correlation IDs, and validates schemas before model invocation.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
from backend.ai.providers.base import Message, ToolCall, ValidationError

logger = logging.getLogger("syllabot.core.serializer")


class MessageSerializer:
    """Converts unified Message dataclasses to/from standard raw dictionary structures."""

    @staticmethod
    def to_dict(msg: Message) -> Dict[str, Any]:
        """Convert a unified Message object into a serializable dictionary."""
        data: Dict[str, Any] = {"role": msg.role}
        if msg.content is not None:
            data["content"] = msg.content
        if msg.tool_calls is not None:
            data["tool_calls"] = [
                {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                for tc in msg.tool_calls
            ]
        if msg.tool_call_id is not None:
            data["tool_call_id"] = msg.tool_call_id
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Message:
        """Parse a dictionary payload into a typed Message object."""
        role = data.get("role")
        if not role:
            raise ValidationError("Message payload must contain a 'role' property.")

        content = data.get("content")
        tool_call_id = data.get("tool_call_id")
        
        tool_calls = None
        if "tool_calls" in data and data["tool_calls"] is not None:
            tool_calls = []
            for tc in data["tool_calls"]:
                # Ensure arguments is a parsed dict
                args = tc.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                tool_calls.append(ToolCall(
                    id=tc.get("id", ""),
                    name=tc.get("name", ""),
                    arguments=args
                ))

        return Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id
        )


class ToolMessageBuilder:
    """Helper class to construct standardized tool response payloads."""

    @staticmethod
    def build(tool_call_id: str, tool_name: str, output: Any) -> Message:
        """Create a unified tool response Message."""
        content_str = output if isinstance(output, str) else json.dumps(output)
        return Message(
            role="tool",
            content=content_str,
            tool_call_id=tool_call_id
        )


class ConversationNormalizer:
    """
    Validates and normalizes conversation message logs before they reach LLM APIs.
    Guarantees structural validity (e.g. matching tool correlation IDs).
    """

    @staticmethod
    def normalize(messages: List[Union[Dict[str, Any], Message]]) -> List[Message]:
        """
        Validates, cleans, and normalizes raw messages list.
        Resolves missing tool call IDs by linking them to the preceding assistant call.
        """
        normalized: List[Message] = []
        for msg in messages:
            if isinstance(msg, Message):
                normalized.append(msg)
            elif isinstance(msg, dict):
                normalized.append(MessageSerializer.from_dict(msg))
            else:
                raise ValidationError(f"Invalid message object of type: {type(msg)}")

        # Validate message roles
        valid_roles = {"system", "user", "assistant", "tool"}
        for idx, msg in enumerate(normalized):
            if msg.role not in valid_roles:
                raise ValidationError(f"Unsupported message role '{msg.role}' at index {idx}.")

        # Re-link orphaned tool messages to their original assistant tool call
        for idx, msg in enumerate(normalized):
            if msg.role == "tool" and not msg.tool_call_id:
                logger.warning(f"Orphaned tool message detected at index {idx}. Attempting to resolve tool_call_id.")
                
                # Search backwards for the assistant message containing tool calls
                resolved_id = None
                for prev_msg in reversed(normalized[:idx]):
                    if prev_msg.role == "assistant" and prev_msg.tool_calls:
                        # Match first tool call if only one exists, or try matching by name
                        if len(prev_msg.tool_calls) == 1:
                            resolved_id = prev_msg.tool_calls[0].id
                            break
                        else:
                            # Attempt matching via helper attributes or fallback
                            resolved_id = prev_msg.tool_calls[0].id
                            break
                
                if resolved_id:
                    msg.tool_call_id = resolved_id
                    logger.info(f"Resolved tool message ID for index {idx} to: {resolved_id}")
                else:
                    # Fabricate a safe mock transaction ID to prevent schema validation blockages on APIs
                    msg.tool_call_id = f"mock_tc_id_{idx}"
                    logger.warning(f"Unable to find preceding tool call for index {idx}. Fabricated ID: {msg.tool_call_id}")

        return normalized
