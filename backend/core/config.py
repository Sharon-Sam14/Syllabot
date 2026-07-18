import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Syllabot"
    API_V1_STR: str = "/api/v1"

    # Database
    # Default to local SQLite, but support environment override
    DATABASE_URL: str = "sqlite:///./syllabot.db"

    # JWT Settings
    # IMPORTANT: In a production environment, this MUST be set as a secure env variable
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production-123456"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
