from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Capstone Defense Scheduler API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://scheduler:scheduler@localhost:5432/scheduler"
    session_cookie_name: str = "scheduler_session"
    session_idle_minutes: int = 15
    session_absolute_hours: int = 8
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

