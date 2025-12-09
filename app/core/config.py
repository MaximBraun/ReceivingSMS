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

    webhook_secret: str

    # OnlineSIM
    onlinesim_api_base_url: str = "https://onlinesim.io"
    onlinesim_api_key: str  # API key из профиля (см. доку auth)
    # на будущее под OAuth2:
    onlinesim_oauth_access_token: str | None = None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()