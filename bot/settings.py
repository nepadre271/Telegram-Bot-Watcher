from typing import Literal
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="SERVICE_"
    )
    disable_sub_system: bool = Field(False)
    join_view_count: int = Field(20)


class PaymentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="PAYMENT_"
    )
    service: Literal["telegram", "yoomoney"] = Field(default="telegram")
    telegram_token: str | None = Field(default=None)
    yoomoney_token: str | None = Field(default=None)


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="TELEGRAM_"
    )
    token: str = Field(...)
    api: str = Field(default="http://telegram-bot-api:8081")
    admins: list[int] = Field(default_factory=list)
    chats_id: list[str] = Field(...)
    bot_id: str = Field(...)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    telegram: TelegramSettings = Field(...)
    payment: PaymentSettings = Field(...)
    service: ServiceSettings = Field(...)
    kinopoisk_token: str = Field(...)
    kinoclub_token: str = Field(...)
    redis_dsn: str = Field("redis://localhost:6379/0")
    uploader_url: str = Field("http://localhost:8000")
    database_dsn: str = Field("sqlite+aiosqlite:///bot.db")
    timezone: str = Field("europe/moscow")
    pwd: Path = Field(Path(__file__).parent.parent.resolve())


payment_settings = PaymentSettings()
service_settings = ServiceSettings()
telegram_settings = TelegramSettings()
settings = Settings(
    telegram=telegram_settings,
    payment=payment_settings,
    service=service_settings
)
