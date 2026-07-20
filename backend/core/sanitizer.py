"""
backend/core/sanitizer.py

Input sanitization for the Syllabot AI pipeline.

Protects against:
  1. Prompt injection — patterns that attempt to override system instructions.
  2. Excessively long inputs — prevents context window abuse and DoS.
  3. Null/empty inputs — returns a cleaned string for downstream processing.

Usage:
    from backend.core.sanitizer import sanitize_input
    clean_message = sanitize_input(user_message)
"""
import logging
import re
from typing import Optional

logger = logging.getLogger("syllabot.core.sanitizer")

# ── Maximum allowed lengths ───────────────────────────────────────────────────
MAX_CHAT_MESSAGE_CHARS = 4000       # AI chat messages
MAX_SYLLABUS_CONTENT_CHARS = 50_000 # Syllabus file content
MAX_NOTE_CHARS = 1000               # Check-in notes


# ── Prompt injection patterns ─────────────────────────────────────────────────
# These patterns attempt to override AI system instructions.
INJECTION_PATTERNS = [
    r"ignore\s+all\s+previous",
    r"disregard\s+all\s+previous",
    r"forget\s+everything\s+you",
    r"act\s+as\s+(?:a|an)?\s*(?:developer|system|programmer)",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+if",
    r"pretend\s+to\s+be",
    r"your\s+new\s+role",
    r"</?system>",
    r"\[system\]",
    r"im_start",
    r"im_end",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def sanitize_input(text: Optional[str], max_length: int = MAX_CHAT_MESSAGE_CHARS) -> str:
    """
    Sanitize a user-provided input string before passing it to the AI pipeline.

    Actions performed:
      1. None / empty → returns empty string.
      2. Strip leading/trailing whitespace.
      3. Truncate to max_length characters with a note appended.
      4. Detect and neutralize prompt injection patterns.

    Args:
        text:       The raw user input.
        max_length: Maximum allowed character length (default: 4000).

    Returns:
        A cleaned, safe string ready for AI processing.
    """
    if not text:
        return ""

    # 1. Strip whitespace
    cleaned = text.strip()

    # 2. Truncate if too long
    if len(cleaned) > max_length:
        logger.warning(
            "Input truncated",
            extra={"original_length": len(cleaned), "max_length": max_length}
        )
        cleaned = cleaned[:max_length] + "... [input truncated]"

    # 3. Detect prompt injection patterns
    for pattern in _compiled_patterns:
        if pattern.search(cleaned):
            logger.warning(
                "Potential prompt injection detected",
                extra={"pattern": pattern.pattern}
            )
            # Neutralize by replacing occurrences of the pattern
            cleaned = pattern.sub("[redacted]", cleaned)

    return cleaned


def sanitize_syllabus_content(text: Optional[str]) -> str:
    """
    Sanitize raw syllabus text before parsing and storage.
    Uses a higher length limit suitable for academic documents.

    Args:
        text: Raw syllabus text content.

    Returns:
        Cleaned text safe for storage and AI processing.
    """
    return sanitize_input(text, max_length=MAX_SYLLABUS_CONTENT_CHARS)


def sanitize_note(text: Optional[str]) -> str:
    """
    Sanitize a check-in note. Uses a lower length limit for user notes.
    """
    return sanitize_input(text, max_length=MAX_NOTE_CHARS)
