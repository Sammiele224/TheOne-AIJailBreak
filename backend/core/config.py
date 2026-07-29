"""Application settings and environment configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and ``backend/.env``."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    deepseek_api_key: str | None = Field(
        default=None,
        validation_alias="DEEPSEEK_API_KEY",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        validation_alias="ANTHROPIC_API_KEY",
    )
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")

    project_name: str = Field(
        default="TheOne AI JailBreak",
        validation_alias="PROJECT_NAME",
    )
    api_v1_str: str = Field(default="/api/v1", validation_alias="API_V1_STR")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    api_key: str | None = Field(default=None, validation_alias="API_KEY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
