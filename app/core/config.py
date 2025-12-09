from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_debug: bool = True

    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str | None = None  # опционально, для отправки SMS

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()