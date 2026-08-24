"""Check representative response keys against the committed wire contract."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_contract import camelize_openapi
from app.main import create_app

SPEC_FILENAME = "openapi.json"
SPEC_PATH = Path(__file__).resolve().parents[1] / SPEC_FILENAME
MANAGER_HEADERS = {"X-Test-Session": "active-manager"}


@dataclass(frozen=True)
class EndpointCase:
    spec_path: str
    url: str
    headers: dict[str, str]


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_camelized_spec_changes_only_wire_keys() -> None:
    source = {
        "info": {"title": "test"},
        "tags": [{"name": "legacy_tag"}],
        "paths": {
            "/api/v1/legacy_path": {
                "get": {
                    "operationId": "legacy_operation",
                    "tags": ["legacy_tag"],
                    "parameters": [
                        {"name": "page_size", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"user_name": {"type": "string"}},
                                    "required": ["user_name"],
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "page_size": {"type": "integer"},
                                            "status_code": {"enum": ["OPEN_REGISTRATION", "S1", "GRP_02"]},
                                            "example_value": {"example": {"raw_key": "keep_me"}},
                                        },
                                        "required": ["page_size"],
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
        "components": {"schemas": {}},
    }

    converted = camelize_openapi(source)
    operation = converted["paths"]["/api/v1/legacy_path"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]

    assert "/api/v1/legacy_path" in converted["paths"]
    assert operation["operationId"] == "legacy_operation"
    assert operation["tags"] == ["legacy_tag"]
    assert operation["parameters"][0]["name"] == "pageSize"
    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
    assert set(request_schema["properties"]) == {"userName"}
    assert request_schema["required"] == ["userName"]
    assert set(schema["properties"]) == {"pageSize", "statusCode", "exampleValue"}
    assert schema["required"] == ["pageSize"]
    assert schema["properties"]["statusCode"]["enum"] == [
        "OPEN_REGISTRATION",
        "S1",
        "GRP_02",
    ]
    assert schema["properties"]["exampleValue"]["example"] == {"raw_key": "keep_me"}


def resolve_schema(spec: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return {}
    reference = schema.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
        name = reference.rsplit("/", 1)[-1]
        return resolve_schema(spec, spec["components"]["schemas"].get(name))
    # An optional field is published as anyOf[<schema>, null], so the branches
    # have to be merged or every key under it would look undocumented.
    for combinator in ("allOf", "anyOf", "oneOf"):
        branches = schema.get(combinator)
        if not isinstance(branches, list):
            continue
        merged: dict[str, Any] = {}
        for item in branches:
            resolved = resolve_schema(spec, item)
            if resolved.get("type") == "null":
                continue
            merged.setdefault("properties", {}).update(resolved.get("properties", {}))
            if "items" in resolved:
                merged["items"] = resolved["items"]
        merged.update({key: value for key, value in schema.items() if key != combinator})
        return merged
    return schema


def response_schema(spec: dict[str, Any], case: EndpointCase, status_code: int) -> dict[str, Any]:
    operation = spec["paths"][case.spec_path]["get"]
    responses = operation["responses"]
    response = responses.get(str(status_code)) or responses.get("default") or {}
    content = response.get("content", {})
    media_type = content.get("application/json", next(iter(content.values()), {}))
    return resolve_schema(spec, media_type.get("schema"))


def assert_payload_keys_match_spec(spec: dict[str, Any], payload: Any, schema: dict[str, Any]) -> None:
    schema = resolve_schema(spec, schema)
    if isinstance(payload, list):
        item_schema = schema.get("items")
        for item in payload:
            assert_payload_keys_match_spec(spec, item, item_schema or {})
        return
    if not isinstance(payload, dict):
        return

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return

    # An open map documents its value type, not its keys, so its keys are data.
    # `additionalProperties: true` only means the model tolerates extras, which is
    # exactly what this test has to report; a schema value means a typed open map.
    additional = schema.get("additionalProperties")
    if additional is not False and not properties:
        return
    if isinstance(additional, dict):
        for name, value in payload.items():
            assert_payload_keys_match_spec(spec, value, properties.get(name, additional))
        return

    unexpected = set(payload) - set(properties)
    assert not unexpected, f"Undocumented response fields: {sorted(unexpected)}"
    for name, value in payload.items():
        assert_payload_keys_match_spec(spec, value, properties[name])


@pytest.mark.parametrize(
    ("case", "method"),
    [
        (EndpointCase("/health", "/health", {}), "get"),
        (EndpointCase("/api/v1/me", "/api/v1/me", MANAGER_HEADERS), "get"),
        (EndpointCase("/api/v1/auth/me", "/api/v1/auth/me", MANAGER_HEADERS), "get"),
    ],
)
def test_local_wire_fields_are_documented(client, case: EndpointCase, method: str) -> None:
    spec = load_spec()
    response = getattr(client, method)(case.url, headers=case.headers)
    assert response.status_code == 200, response.text
    assert_payload_keys_match_spec(spec, response.json(), response_schema(spec, case, response.status_code))


@pytest.fixture(scope="module")
def seeded_client():
    with TestClient(create_app()) as test_client:
        response = test_client.post(
            "/api/v1/admin/seed-fixture",
            headers={"X-Test-Session": "active-admin"},
        )
        assert response.status_code == 201, response.text
        yield test_client


@pytest.mark.integration
@pytest.mark.parametrize(
    "case",
    [
        EndpointCase("/api/v1/semesters", "/api/v1/semesters", MANAGER_HEADERS),
        EndpointCase("/api/v1/projects", "/api/v1/projects", MANAGER_HEADERS),
        EndpointCase("/api/v1/groups", "/api/v1/groups", MANAGER_HEADERS),
        EndpointCase("/api/v1/lecturers", "/api/v1/lecturers", MANAGER_HEADERS),
        EndpointCase("/api/v1/rooms", "/api/v1/rooms", MANAGER_HEADERS),
        EndpointCase("/api/v1/committees", "/api/v1/committees", MANAGER_HEADERS),
        EndpointCase("/api/v1/timeframes", "/api/v1/timeframes", MANAGER_HEADERS),
        EndpointCase("/api/v1/dashboard", "/api/v1/dashboard", MANAGER_HEADERS),
        EndpointCase(
            "/api/v1/my/rounds",
            "/api/v1/my/rounds",
            {"X-Test-Session": "active-student"},
        ),
        EndpointCase("/api/v1/semesters/{semesterId}", "/api/v1/semesters/999999", MANAGER_HEADERS),
    ],
)
def test_committed_spec_matches_live_wire(seeded_client, case: EndpointCase) -> None:
    spec = load_spec()
    response = seeded_client.get(case.url, headers=case.headers)
    assert response.status_code in {200, 404}, response.text
    assert_payload_keys_match_spec(spec, response.json(), response_schema(spec, case, response.status_code))
