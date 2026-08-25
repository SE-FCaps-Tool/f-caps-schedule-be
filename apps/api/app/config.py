from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Capstone Defense Scheduler API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://scheduler:scheduler@localhost:5432/scheduler"
    session_cookie_name: str = "scheduler_session"
    # The readable CSRF cookie must be visible to the separate frontend
    # subdomain so the FE can echo it in X-CSRF-Token. Keep the session cookie
    # host-only/HttpOnly; only set this in deployments that share a parent
    # domain with the frontend (for example, .f-caps.net).
    cookie_domain: str = ""
    session_idle_minutes: int = 60
    session_absolute_hours: int = 168
    frontend_url: str = "http://localhost:5173"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    semester_min_duration_days: int = 105
    semester_max_duration_days: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
