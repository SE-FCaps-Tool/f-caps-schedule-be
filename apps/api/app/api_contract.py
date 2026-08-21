"""Machine-readable target API contract and shared payload helpers.

The registry is intentionally independent from route decorators.  It gives the
frontend migration a stable inventory while legacy handlers are migrated in
bounded phases.  Route implementations can reference this metadata without
making the registry the source of runtime authorization decisions.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

EnvelopeDataT = TypeVar("EnvelopeDataT")

# Public identifiers are deliberately opaque to the frontend while the
# database continues to use integer primary keys.  Keep this codec in one
# place so every target route accepts both migration-era integers and the
# documented ``prefix_number`` form.
TARGET_ID_PREFIXES: tuple[str, ...] = (
    "grp_", "prj_", "rnd_", "lec_", "stu_", "sv_", "ses_", "room_", "ts_", "inv_", "rem_"
)


def parse_external_id(value: Any, *, prefix: str | None = None) -> int:
    """Resolve a legacy integer or target external id to a database id.

    ``prefix`` may be supplied with or without the trailing underscore.  A
    stable ``ValueError`` is used so route adapters can translate malformed
    values to their normal validation envelope.
    """

    if isinstance(value, bool):
        raise TypeError("identifier must be an integer or prefixed string")
    if isinstance(value, int):
        if value > 0:
            return value
        raise ValueError("identifier must be positive")
    raw = str(value).strip()
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    expected = None if prefix is None else prefix.rstrip("_") + "_"
    match = re.fullmatch(r"([a-z][a-z0-9]*)_(\d+)", raw, flags=re.IGNORECASE)
    if match is None or int(match.group(2)) <= 0:
        raise ValueError("identifier must be an integer or prefixed string")
    if expected is not None and match.group(1).lower() + "_" != expected.lower():
        raise ValueError(f"identifier must use prefix {expected}")
    return int(match.group(2))


def external_id(value: Any, prefix: str) -> str:
    """Serialize a database id as the documented prefixed target id."""

    number = parse_external_id(value)
    normalized = prefix.rstrip("_") + "_"
    return f"{normalized}{number}"


def target_id_fields(value: Any, prefix: str, *fields: str) -> dict[str, Any]:
    """Return a small mapping useful when adapting SQL rows for target DTOs."""

    result = dict(value) if isinstance(value, Mapping) else {}
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = external_id(result[field], prefix)
    return result


@dataclass(frozen=True)
class ApiOperation:
    method: str
    path: str
    request_body_schema: str
    success_status: int
    success_schema: str
    roles: tuple[str, ...]
    paginated: bool = False
    alias_of: str | None = None


def _op(
    method: str,
    path: str,
    *,
    schema: str = "object",
    roles: tuple[str, ...] = ("MANAGER",),
    paginated: bool = False,
    alias_of: str | None = None,
) -> ApiOperation:
    return ApiOperation(
        method=method,
        path=path,
        request_body_schema="none" if method == "GET" else "json",
        success_status=201 if method == "POST" and path.endswith("/invitations") else 200,
        success_schema=schema,
        roles=roles,
        paginated=paginated,
        alias_of=alias_of,
    )


# 54 target method/path declarations from the implementation spec.  Keep this
# list explicit so a missing operation is visible in review and OpenAPI checks.
TARGET_OPERATIONS: tuple[ApiOperation, ...] = (
    # Group/project resources.
    _op("GET", "/api/v1/groups/{groupId}"),
    _op("GET", "/api/v1/groups/{groupId}/members", schema="array", paginated=True),
    _op("POST", "/api/v1/groups/{groupId}/actions/change-leader"),
    _op("POST", "/api/v1/groups/{groupId}/members/{memberId}/actions/leave"),
    _op("PUT", "/api/v1/groups/{groupId}/project"),
    _op("GET", "/api/v1/projects/{projectId}"),
    _op("GET", "/api/v1/projects/{projectId}/progression"),
    _op("GET", "/api/v1/projects/{projectId}/results", schema="array", paginated=True),
    _op("GET", "/api/v1/semesters/{semesterId}/groups", schema="array", paginated=True),
    _op("POST", "/api/v1/semesters/{semesterId}/groups"),
    _op("GET", "/api/v1/semesters/{semesterId}/projects", schema="array", paginated=True),
    _op("POST", "/api/v1/semesters/{semesterId}/projects"),
    # Round lifecycle, registration, invitation, availability.
    _op("GET", "/api/v1/rounds/{roundId}"),
    _op("PATCH", "/api/v1/rounds/{roundId}"),
    _op("GET", "/api/v1/rounds/{roundId}/eligible-projects", schema="array", paginated=True),
    _op("GET", "/api/v1/rounds/{roundId}/groups/{groupId}/preferences"),
    _op("PUT", "/api/v1/rounds/{roundId}/groups/{groupId}/preferences"),
    _op("GET", "/api/v1/rounds/{roundId}/invitations", schema="array", paginated=True),
    _op("POST", "/api/v1/rounds/{roundId}/invitations"),
    _op("POST", "/api/v1/rounds/{roundId}/invitations/me/respond", roles=("LECTURER",)),
    _op("POST", "/api/v1/rounds/{roundId}/invitations/{invitationId}/remind"),
    _op("PUT", "/api/v1/rounds/{roundId}/availability/me", roles=("LECTURER", "STUDENT")),
    _op("GET", "/api/v1/rounds/{roundId}/availability/me", roles=("LECTURER", "STUDENT")),
    _op("GET", "/api/v1/rounds/{roundId}/registration-summary"),
    _op("GET", "/api/v1/rounds/{roundId}/scheduling-readiness"),
    _op("POST", "/api/v1/rounds/{roundId}/actions/open-registration"),
    _op("POST", "/api/v1/rounds/{roundId}/actions/close-registration"),
    _op("GET", "/api/v1/semesters/{semesterId}/rounds", schema="array", paginated=True),
    _op("POST", "/api/v1/semesters/{semesterId}/rounds"),
    # Schedule versions, sessions, rooms, and publication.
    _op("GET", "/api/v1/rounds/{roundId}/schedules", schema="array", paginated=True),
    _op("POST", "/api/v1/rounds/{roundId}/schedules/generate"),
    _op("GET", "/api/v1/rounds/{roundId}/schedules/{scheduleId}"),
    _op("POST", "/api/v1/rounds/{roundId}/schedules/{scheduleId}/actions/discard"),
    _op("POST", "/api/v1/rounds/{roundId}/schedules/{scheduleId}/actions/set-active"),
    _op("GET", "/api/v1/rounds/{roundId}/sessions", schema="array", paginated=True),
    _op("GET", "/api/v1/rounds/{roundId}/publish-readiness"),
    _op("POST", "/api/v1/rounds/{roundId}/actions/publish"),
    _op("GET", "/api/v1/rounds/{roundId}/rooms/available", schema="array", paginated=True),
    _op("POST", "/api/v1/rounds/{roundId}/rooms/suggest"),
    _op("POST", "/api/v1/rounds/{roundId}/rooms/apply-suggestions"),
    _op("GET", "/api/v1/sessions/{sessionId}"),
    _op("POST", "/api/v1/sessions/{sessionId}/actions/change-room"),
    _op("POST", "/api/v1/sessions/{sessionId}/actions/postpone"),
    _op("POST", "/api/v1/sessions/{sessionId}/actions/replace-reviewer"),
    _op("POST", "/api/v1/sessions/{sessionId}/makeup"),
    _op("POST", "/api/v1/sessions/{sessionId}/result"),
    _op("PUT", "/api/v1/sessions/{sessionId}/room"),
    # Lecturer and leader portals.
    _op("GET", "/api/v1/lecturer/me/invitations", schema="array", roles=("LECTURER",), paginated=True),
    _op("GET", "/api/v1/lecturer/me/remediations", schema="array", roles=("LECTURER",), paginated=True),
    _op("GET", "/api/v1/lecturer/me/sessions", schema="array", roles=("LECTURER",), paginated=True),
    _op("GET", "/api/v1/lecturer/me/supervised-projects", schema="array", roles=("LECTURER",), paginated=True),
    _op("GET", "/api/v1/leader/me/dashboard", roles=("STUDENT",)),
    _op("GET", "/api/v1/leader/me/sessions", schema="array", roles=("STUDENT",), paginated=True),
    # Results and remediation.
    _op("POST", "/api/v1/remediations/{remediationId}/verify", roles=("LECTURER", "MANAGER")),
)


# Checklist extension tracked alongside, but not counted as, the 53 operations
# explicitly declared in the implementation spec.
CHECKLIST_OPERATIONS: tuple[ApiOperation, ...] = (
    _op("GET", "/api/v1/semesters/{semesterId}/remediations", schema="array", paginated=True),
)


def _camel_case_key(key: str) -> str:
    if "_" not in key:
        return key
    head, *rest = key.split("_")
    return head + "".join(word[:1].upper() + word[1:] for word in rest if word)


def camelize(value: Any) -> Any:
    """Recursively convert snake_case dict keys to camelCase.

    Target routes build response bodies from legacy snake_case SQL rows and
    domain dicts; this is the single conversion point so individual routes
    don't have to hand-rename every field to match the spec's camelCase
    convention.
    """

    if isinstance(value, Mapping):
        return {_camel_case_key(k) if isinstance(k, str) else k: camelize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [camelize(item) for item in value]
    if isinstance(value, tuple):
        return tuple(camelize(item) for item in value)
    return value


def success_payload(data: Any, *, meta: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return the target success envelope with camelCase field names."""

    payload: dict[str, Any] = {"data": camelize(data)}
    if meta is not None:
        payload["meta"] = camelize(dict(meta))
    return payload


class PaginationMeta(BaseModel):
    page: int = 1
    page_size: int = Field(default=20, alias="pageSize")
    total: int = 0

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ApiDataEnvelope(BaseModel, Generic[EnvelopeDataT]):
    data: EnvelopeDataT
    meta: PaginationMeta | None = None


class ApiErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiErrorEnvelope(BaseModel):
    error: ApiErrorBody

    def __init__(self, *, code: str | None = None, message: str | None = None, details: dict[str, Any] | None = None, **data: Any):
        if code is not None or message is not None:
            data["error"] = ApiErrorBody(code=code or "UNKNOWN_ERROR", message=message or "Request failed.", details=details or {})
        super().__init__(**data)


def error_payload(code: str, message: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return the target structured error envelope."""

    return {
        "error": {
            "code": code,
            "message": message,
            "details": dict(details or {}),
        }
    }


def legacy_contract_headers(path: str) -> dict[str, str]:
    """Return deprecation metadata for known legacy route shapes."""

    successor: str | None = None
    if path == "/api/v1/groups":
        successor = "/api/v1/semesters/{semesterId}/groups"
    elif path == "/api/v1/projects":
        successor = "/api/v1/semesters/{semesterId}/projects"
    elif path == "/api/v1/rounds":
        successor = "/api/v1/semesters/{semesterId}/rounds"
    elif re.fullmatch(r"/api/v1/rounds/[^/]+/schedule/run", path):
        successor = path.replace("/schedule/run", "/schedules/generate")
    elif re.fullmatch(r"/api/v1/rounds/[^/]+/schedule/versions", path):
        successor = path.replace("/schedule/versions", "/schedules")
    elif path.startswith("/api/v1/schedule/versions/"):
        successor = "/api/v1/rounds/{roundId}/schedules/{scheduleId}"
    elif path.startswith("/api/v1/my/"):
        successor = "/api/v1/lecturer/me/* or /api/v1/leader/me/*"
    elif path.startswith("/api/v1/remediation"):
        successor = "/api/v1/remediations/{remediationId}/*"
    if successor is None:
        return {}
    return {
        "Deprecation": "true",
        "Sunset": "Wed, 31 Dec 2026 23:59:59 GMT",
        "Link": f'<{successor}>; rel="successor-version"',
    }
