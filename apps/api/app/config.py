from functools import lru_cache

from pydantic import model_validator
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
    session_heartbeat_seconds: int = 60
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

    @model_validator(mode="after")
    def _clamp_heartbeat_window(self) -> "Settings":
        # A heartbeat window at or above the idle window means a session's
        # last_seen_at write never lands before the idle-timeout SELECT would
        # already reject it — every session then dies at idle timeout
        # regardless of activity. Keep it well under the idle window.
        max_heartbeat = max(1, (self.session_idle_minutes * 60) // 2)
        if not (0 < self.session_heartbeat_seconds <= max_heartbeat):
            self.session_heartbeat_seconds = min(max(self.session_heartbeat_seconds, 1), max_heartbeat)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
