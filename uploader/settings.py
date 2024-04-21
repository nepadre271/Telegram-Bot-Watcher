from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    telegram_token: str = Field(...)
    telegram_timeout: int = Field(60 * 15)
    telegram_api: str = Field("http://telegram-bot-api:8081")
    kinoclub_token: str = Field(...)
    temp_chat_id: str = Field(...)
    redis_dsn: str = Field("redis://localhost:6379/0")
    

settings = Settings()
