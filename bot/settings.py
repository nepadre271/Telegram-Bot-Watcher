from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    token: str = Field(..., alias="TELEGRAM_TOKEN")
    api: str = Field(default="http://telegram-bot-api:8081", alias="TELEGRAM_API_URL")
    admins: list[int] = Field(default_factory=list, alias="TELEGRAM_ADMINS")
    payments_token: str = Field(..., alias="TELEGRAM_PAYMENTS_TOKEN")
    chats_id: list[str] = Field(..., alias="TELEGRAM_CHATS_ID")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    telegram: TelegramSettings = Field(...)
    kinopoisk_token: str = Field(...)
    kinoclub_token: str = Field(...)
    redis_dsn: str = Field("redis://localhost:6379/0")
    uploader_url: str = Field("http://localhost:8000")
    database_dsn: str = Field("sqlite+aiosqlite:///bot.db")
    timezone: str = Field("europe/moscow")
    pwd: Path = Field(Path(__file__).parent.parent.resolve())


telegram_settings = TelegramSettings()
settings = Settings(telegram=telegram_settings)
