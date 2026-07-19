from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    AI_PROVIDER: str = "openai"  # default to openai, can be gemini, groq, claude
    AI_MODEL: Optional[str] = None  # if not specified, default based on provider

    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


ai_settings = AISettings()
