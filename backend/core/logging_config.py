"""
backend/core/logging_config.py

Structured JSON logging for Syllabot.
Configures the root logger to emit JSON-formatted log lines using
python-json-logger. This enables log aggregation tools (Datadog, Loki, etc.)
to parse and index logs as structured data.

Usage:
    from backend.core.logging_config import setup_logging
    setup_logging()  # Called once at app startup in main.py
"""
import logging
import sys
from typing import Optional

from backend.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure the root logger with JSON structured output.

    Args:
        log_level: Override log level. Defaults to settings.LOG_LEVEL.
    """
    level_str = (log_level or settings.LOG_LEVEL).upper()
    level = getattr(logging, level_str, logging.INFO)

    # Try to use python-json-logger if available; fall back to standard formatter
    try:
        from pythonjsonlogger import jsonlogger

        class SyllabotJsonFormatter(jsonlogger.JsonFormatter):
            """
            Custom JSON formatter that adds a 'service' field to every log line.
            """
            def add_fields(self, log_record, record, message_dict):
                super().add_fields(log_record, record, message_dict)
                log_record["service"] = "syllabot"
                log_record["level"] = record.levelname
                log_record["logger"] = record.name

        formatter = SyllabotJsonFormatter(
            fmt="%(asctime)s %(level)s %(name)s %(message)s"
        )
    except ImportError:
        # Graceful fallback if python-json-logger is not installed yet
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        )

    # Configure the root handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if called multiple times (e.g., during tests)
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    # Reduce noise from verbose third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger("syllabot.logging")
    logger.info(
        "Structured logging initialized",
        extra={"log_level": level_str}
    )


def get_logger(name: str) -> logging.Logger:
    """
    Convenience factory for named module loggers.
    All Syllabot loggers should use the 'syllabot.' prefix.

    Example:
        logger = get_logger("syllabot.ai.agent")
    """
    return logging.getLogger(name)
