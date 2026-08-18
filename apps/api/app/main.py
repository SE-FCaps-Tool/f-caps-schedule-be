import hashlib
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from .auth import CurrentUser, get_current_user
from .config import get_settings
from .database import get_engine
from .routes.auth_routes import router as auth_router
from .routes.master_data import router as master_data_router
from .routes.operations import router as operations_router
from .routes.results import router as results_router
from .routes.schedule_operations import router as schedule_operations_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    @app.middleware("http")
    async def csrf_guard(request: Request, call_next):
        mutating = request.method in {"POST", "PUT", "PATCH", "DELETE"}
        cookie_session = request.cookies.get(settings.session_cookie_name)
        exempt = request.url.path in {"/api/v1/auth/login", "/api/v1/auth/logout"}
        if mutating and cookie_session and not exempt:
            csrf_cookie = request.cookies.get("scheduler_csrf")
            csrf_header = request.headers.get("X-CSRF-Token")
            if not _valid_csrf(settings, session_token=cookie_session, cookie_value=csrf_cookie, header_value=csrf_header):
                response = JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=()")
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; connect-src 'self' https:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'")
        if settings.app_env not in {"development", "test"}:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
    app.include_router(master_data_router)
    app.include_router(schedule_operations_router)
    app.include_router(results_router)
    app.include_router(operations_router)
    app.include_router(auth_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "api"}

    @app.get("/api/v1/me", tags=["auth"])
    def me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> dict[str, str]:
        return {"role": user.role, "status": user.status}

    return app


def _valid_csrf(settings, *, session_token: str | None, cookie_value: str | None, header_value: str | None) -> bool:
    if not session_token or not cookie_value or not header_value or cookie_value != header_value:
        return False
    with Session(get_engine(settings.database_url)) as db:
        stored_hash = db.execute(
            text("SELECT csrf_token_hash FROM auth_sessions WHERE token_hash = :token_hash AND revoked_at IS NULL AND expires_at > now()"),
            {"token_hash": hashlib.sha256(session_token.encode()).hexdigest()},
        ).scalar_one_or_none()
    return stored_hash == hashlib.sha256(header_value.encode()).hexdigest()


app = create_app()
