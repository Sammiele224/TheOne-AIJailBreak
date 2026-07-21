from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str | None = None
    openai_api_key: str | None = None
    deepseek_api_key: str | None = None

    database_url: str | None = None


settings = Settings()
