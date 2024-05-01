from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    tg_token: str = Field(..., alias="TELEGRAM_TOKEN")
    tg_timeout: int = Field(60 * 15, alias="TELEGRAM_TIMEOUT")
    kinopoisk_token: str = Field(...)
    kinoclub_token: str = Field(...)
    chat_url: str = Field(...)
    chat_id: str = Field(...)
    temp_chat_id: str = Field(...)
    redis_dsn: str = Field("redis://localhost:6379/0")
    uploader_url: str = Field("http://localhost:8000")
    

settings = Settings()
