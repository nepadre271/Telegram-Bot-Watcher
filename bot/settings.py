from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    tg_token: str = Field(..., alias="TELEGRAM_TOKEN")
    tg_timeout: int = Field(60 * 5, alias="TELEGRAM_TIMEOUT")
    kp_token: str = Field(..., alias="KP_TOKEN")
    kinoclub_token: str = Field(..., alias="KINOCLUB_TOKEN")
    chat_url: str = Field(..., alias="CHAT_URL")
    chat_id: str = Field(..., alias="CHAT_ID")
    redis_dsn: str = Field("redis://localhost:6379")
    

settings = Settings()
