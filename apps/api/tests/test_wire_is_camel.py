"""Contract guard for camelCase response fields.

The committed OpenAPI document is the inventory of the public wire contract.  This
test walks only response schemas, resolves local component references, and fails
when a response property is written in the legacy snake_case form.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

SNAKE_KEY = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")
SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi.json"
COMPOSITION_KEYS = ("allOf", "anyOf", "oneOf", "prefixItems")
NESTED_SCHEMA_KEYS = (
    "additionalProperties",
    "contains",
    "contentSchema",
    "else",
    "if",
    "items",
    "not",
    "propertyNames",
    "then",
    "unevaluatedItems",
    "unevaluatedProperties",
)


def _load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def _resolve_local_ref(spec: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        return None
    current: Any = spec
    for part in reference[2:].split("/"):
        if not isinstance(current, dict):
            return None
        current = current.get(part.replace("~1", "/").replace("~0", "~"))
    return current


def _snake_response_keys(spec: dict[str, Any]) -> Iterator[str]:
    seen: set[int] = set()

    def walk(value: Any) -> Iterator[str]:
        if not isinstance(value, dict):
            if isinstance(value, list):
                for item in value:
                    yield from walk(item)
            return

        marker = id(value)
        if marker in seen:
            return
        seen.add(marker)

        reference = value.get("$ref")
        if isinstance(reference, str):
            resolved = _resolve_local_ref(spec, reference)
            if resolved is not None:
                yield from walk(resolved)

        properties = value.get("properties")
        if isinstance(properties, dict):
            for name, schema in properties.items():
                if isinstance(name, str) and SNAKE_KEY.fullmatch(name):
                    yield name
                yield from walk(schema)

        for key in COMPOSITION_KEYS:
            branch = value.get(key)
            if isinstance(branch, list):
                for item in branch:
                    yield from walk(item)
        for key in NESTED_SCHEMA_KEYS:
            if key in value:
                yield from walk(value[key])

    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        return
    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            responses = operation.get("responses", {})
            if not isinstance(responses, dict):
                continue
            for response in responses.values():
                if not isinstance(response, dict):
                    continue
                content = response.get("content", {})
                if not isinstance(content, dict):
                    continue
                for media_type in content.values():
                    if isinstance(media_type, dict):
                        yield from walk(media_type.get("schema"))


def test_every_response_property_is_camel_case() -> None:
    snake_keys = sorted(set(_snake_response_keys(_load_spec())))
    assert not snake_keys, f"snake_case response properties found: {snake_keys}"


def test_guard_detects_a_new_snake_case_response_property() -> None:
    """Keep the guard meaningful: a synthetic endpoint must be rejected."""

    spec = copy.deepcopy(_load_spec())
    spec.setdefault("paths", {})["/__contract_probe"] = {
        "get": {
            "responses": {
                "200": {
                    "description": "probe",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"legacy_field": {"type": "string"}},
                            }
                        }
                    },
                }
            }
        }
    }

    assert "legacy_field" in set(_snake_response_keys(spec))
