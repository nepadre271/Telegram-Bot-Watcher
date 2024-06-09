from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    telegram_token: str = Field(..., alias="TELEGRAM_TOKEN")
    telegram_timeout: int = Field(60 * 15, alias="TELEGRAM_TIMEOUT")
    telegram_api: str = Field(default="http://telegram-bot-api:8081")
    telegram_admins: list[int] = Field(default_factory=list)
    telegram_payments_token: str = Field(...)
    kinopoisk_token: str = Field(...)
    kinoclub_token: str = Field(...)
    chat_url: str = Field(...)
    chat_id: str = Field(...)
    temp_chat_id: str = Field(...)
    redis_dsn: str = Field("redis://localhost:6379/0")
    uploader_url: str = Field("http://localhost:8000")
    database_dsn: str = Field("sqlite+aiosqlite:///bot.db")
    timezone: str = Field("europe/moscow")
    

settings = Settings()
