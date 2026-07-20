import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Unified application settings for Syllabot.
    All configuration is read from environment variables or the .env file.
    See .env.example for documentation on each variable.
    """

    # ── Project ──────────────────────────────────────────────
    PROJECT_NAME: str = "Syllabot"
    API_V1_STR: str = "/api/v1"

    # ── Database ──────────────────────────────────────────────
    # Supports SQLite (development) and PostgreSQL (production).
    # Format for PostgreSQL: postgresql+psycopg2://user:pass@host:5432/dbname
    DATABASE_URL: str = "sqlite:///./syllabot.db"

    # ── JWT Authentication ────────────────────────────────────
    # IMPORTANT: Override JWT_SECRET_KEY with a secure random value in production.
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production-123456"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ── CORS / URLs ───────────────────────────────────────────
    # FRONTEND_URL is used to lock CORS in production.
    # Leave empty to allow all origins (development only).
    FRONTEND_URL: Optional[str] = None
    BACKEND_URL: str = "http://localhost:8000"

    # ── AI Providers ──────────────────────────────────────────
    # The active provider used as the default for the legacy LLMService.
    # The LangGraph ModelRouter selects the provider per-task automatically.
    AI_PROVIDER: str = "gemini"

    # Optional: pin a specific model. If empty, smart defaults are used.
    AI_MODEL: Optional[str] = None

    # Gemini (Google AI Studio) — semantic reasoning, parsing, general chat
    # Get key at: https://aistudio.google.com/app/apikey
    GEMINI_API_KEY: Optional[str] = None

    # Groq — fast inference, plan generation, quiz generation, summaries
    # Get key at: https://console.groq.com/keys
    GROQ_API_KEY: Optional[str] = None

    # Legacy providers — kept for backward compatibility
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    # ── Observability ─────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
