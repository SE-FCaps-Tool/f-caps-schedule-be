import hashlib
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from .api_contract import error_payload, legacy_contract_headers
from .auth import CurrentUser, get_current_user
from .config import get_settings
from .database import get_engine
from .response_models import HealthResponse, PublicMeResponse
from .routes.auth_routes import router as auth_router
from .routes.manager_extensions import router as manager_extensions_router
from .routes.master_data import router as master_data_router
from .routes.operations import router as operations_router
from .routes.results import router as results_router
from .routes.room_assignment import router as room_assignment_router
from .routes.schedule_operations import router as schedule_operations_router
from .routes.target_group_project import router as target_group_project_router
from .routes.target_operations import router as target_operations_router
from .routes.target_portals import router as target_portals_router
from .routes.target_results_remediation import router as target_results_remediation_router
from .routes.target_room_publish import router as target_room_publish_router
from .routes.target_round_contract import router as target_round_contract_router
from .routes.target_schedule_contract import router as target_schedule_contract_router
from .services.route_telemetry import record_route_usage


def _is_target_route(request: Request) -> bool:
    """True when the matched route belongs to a ``target_*`` contract router.

    Legacy routes keep their existing ``{"detail": ...}`` error shape during
    the migration (see plan.md's compatibility policy); only routes tagged
    ``target-*`` switch to the spec's ``{"error": {...}}`` envelope.
    """

    route = request.scope.get("route")
    tags = getattr(route, "tags", None) or []
    return any(str(tag).startswith("target-") for tag in tags)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", docs_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    swagger_assets = Path(__file__).with_name("static") / "swagger"
    app.mount("/_docs", StaticFiles(directory=swagger_assets), name="swagger-assets")

    @app.get("/docs", include_in_schema=False)
    def swagger_ui() -> HTMLResponse:
        return HTMLResponse(
            """
            <!doctype html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="stylesheet" href="/_docs/swagger-ui.css" />
                <title>Capstone Defense Scheduler API - Swagger UI</title>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="/_docs/swagger-ui-bundle.js"></script>
                <script src="/_docs/swagger-ui-init.js"></script>
            </body>
            </html>
            """
        )

    @app.get("/docs/oauth2-redirect", include_in_schema=False)
    def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()

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

    @app.middleware("http")
    async def legacy_contract_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        record_route_usage(request.method, request.url.path)
        for key, value in legacy_contract_headers(request.url.path).items():
            response.headers.setdefault(key, value)
        return response
    app.include_router(master_data_router)
    app.include_router(manager_extensions_router)
    app.include_router(schedule_operations_router)
    app.include_router(target_group_project_router)
    app.include_router(target_round_contract_router)
    app.include_router(target_schedule_contract_router)
    app.include_router(target_room_publish_router)
    app.include_router(target_operations_router)
    app.include_router(target_results_remediation_router)
    app.include_router(target_portals_router)
    app.include_router(results_router)
    app.include_router(room_assignment_router)
    app.include_router(operations_router)
    app.include_router(auth_router)

    @app.exception_handler(HTTPException)
    async def _target_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if not _is_target_route(request):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code", "HTTP_ERROR"))
            message = str(detail.get("message", code))
            raw_details = detail.get("details")
            details = raw_details if isinstance(raw_details, dict) else {}
        else:
            code = "HTTP_ERROR"
            message = str(detail)
            details = {}
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(code, message, details=details),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _target_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        if not _is_target_route(request):
            return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})
        return JSONResponse(
            status_code=422,
            content=error_payload(
                "VALIDATION_ERROR",
                "Request validation failed.",
                details={"errors": jsonable_encoder(exc.errors())},
            ),
        )

    @app.get("/health", tags=["system"], response_model=HealthResponse)
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "api"}

    @app.get("/api/v1/me", tags=["auth"], response_model=PublicMeResponse)
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
