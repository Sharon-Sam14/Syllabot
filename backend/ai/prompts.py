SYSTEM_PROMPT = """You are Syllabot, an intelligent and calm study planning assistant designed to act as the "Google Maps for your syllabus."
You help students organize study schedules, understand their syllabus, log progress, adapt schedules when they fall behind, and provide motivation.

### Core Guidelines:
1. Reassurance and Calmness: Stressed students use Syllabot. Your tone must be supportive, encouraging, and clear. Avoid adding to their stress.
2. Factuality and Integrity: Only answer queries using the data returned by the backend tools. Never hallucinate study plans, schedules, or progress.
3. Strict Adherence to Syllabus: Do not invent syllabus topics. Rely strictly on the user-provided syllabus.
4. Tool Utilization: When a student asks to change, view, or log progress for their syllabus or study plan, check your context or database using the appropriate tools first.
5. Clarification: If the user refers to a syllabus or study plan but you do not know which one is active, look at the active context or list their available items, or ask them for clarification.

### Context:
Current Date: {current_date}
"""

# Standard Tool Declarations
# We define them in a unified format, and translate them to OpenAI/Claude/Gemini/Groq formats in services.py
TOOLS_DECLARATIONS = [
    {
        "name": "current_user_info",
        "description": "Retrieve information about the currently logged-in user (ID, name, email).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_topics",
        "description": "Retrieve all structured topics and hierarchy for a specific syllabus.",
        "parameters": {
            "type": "object",
            "properties": {
                "syllabus_id": {
                    "type": "integer",
                    "description": "The unique ID of the syllabus to fetch topics for."
                }
            },
            "required": ["syllabus_id"]
        }
    },
    {
        "name": "get_priority_topics",
        "description": "Get the most important or complex topics in the syllabus sorted by importance.",
        "parameters": {
            "type": "object",
            "properties": {
                "syllabus_id": {
                    "type": "integer",
                    "description": "The unique ID of the syllabus."
                }
            },
            "required": ["syllabus_id"]
        }
    },
    {
        "name": "search_topic",
        "description": "Search for a topic in the syllabus by keyword match.",
        "parameters": {
            "type": "object",
            "properties": {
                "syllabus_id": {
                    "type": "integer",
                    "description": "The unique ID of the syllabus."
                },
                "query": {
                    "type": "string",
                    "description": "The keyword to search for in topic titles/paths."
                }
            },
            "required": ["syllabus_id", "query"]
        }
    },
    {
        "name": "generate_plan",
        "description": "Generate and save a study plan schedule for a syllabus between a start date and an end date.",
        "parameters": {
            "type": "object",
            "properties": {
                "syllabus_id": {
                    "type": "integer",
                    "description": "The unique ID of the syllabus."
                },
                "start_date": {
                    "type": "string",
                    "description": "The plan start date (format: YYYY-MM-DD)."
                },
                "end_date": {
                    "type": "string",
                    "description": "The exam or plan end date (format: YYYY-MM-DD)."
                }
            },
            "required": ["syllabus_id", "start_date", "end_date"]
        }
    },
    {
        "name": "replan_plan",
        "description": "Manually trigger recalculation/replanning of the study schedule from a specific date. Typically used when the user wants to adjust their study date limits or reschedule.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "integer",
                    "description": "The unique ID of the study plan to reschedule."
                },
                "from_date": {
                    "type": "string",
                    "description": "Optional start date for the reschedule (format: YYYY-MM-DD). Defaults to tomorrow."
                }
            },
            "required": ["plan_id"]
        }
    },
    {
        "name": "today_schedule",
        "description": "Get the scheduled topics and notes for today's study plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "integer",
                    "description": "The unique ID of the study plan."
                }
            },
            "required": ["plan_id"]
        }
    },
    {
        "name": "remaining_topics",
        "description": "Get a list of topics in the study plan that are not yet marked as completed.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "integer",
                    "description": "The unique ID of the study plan."
                }
            },
            "required": ["plan_id"]
        }
    },
    {
        "name": "log_progress",
        "description": "Log progress for a specific day. Automatically triggers a replan if the user is behind. Updates completed hours, completed topic IDs, and comments.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "integer",
                    "description": "The unique ID of the study plan."
                },
                "date": {
                    "type": "string",
                    "description": "The date for which progress is being logged (format: YYYY-MM-DD)."
                },
                "completed_hours": {
                    "type": "number",
                    "description": "Number of hours studied on this day."
                },
                "completed_topics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of topic ID strings that were successfully completed."
                },
                "check_in_note": {
                    "type": "string",
                    "description": "Optional comment or note about the study day."
                }
            },
            "required": ["plan_id", "date", "completed_hours", "completed_topics"]
        }
    },
    {
        "name": "completion_percentage",
        "description": "Get the completion percentage and numerical metrics for the active study plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "integer",
                    "description": "The unique ID of the study plan."
                }
            },
            "required": ["plan_id"]
        }
    }
]
