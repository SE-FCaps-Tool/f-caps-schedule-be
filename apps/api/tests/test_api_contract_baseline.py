from app.api_contract import TARGET_OPERATIONS, error_payload, success_payload


def test_target_registry_contains_unique_complete_operations():
    keys = [(operation.method, operation.path) for operation in TARGET_OPERATIONS]

    assert len(TARGET_OPERATIONS) == 53
    assert len(set(keys)) == len(keys)
    for operation in TARGET_OPERATIONS:
        assert operation.method in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        assert operation.path.startswith("/api/v1/")
        assert operation.request_body_schema
        assert operation.success_schema
        assert 200 <= operation.success_status < 300
        assert operation.roles
        assert operation.alias_of is None or operation.alias_of.startswith("/api/v1/")


def test_success_payload_supports_data_and_pagination_metadata():
    assert success_payload({"id": "1"}) == {"data": {"id": "1"}}
    assert success_payload([{"id": "1"}], meta={"page": 1, "pageSize": 20}) == {
        "data": [{"id": "1"}],
        "meta": {"page": 1, "pageSize": 20},
    }


def test_error_payload_has_stable_code_message_and_details():
    assert error_payload("ROUND_NOT_FOUND", "Round does not exist.") == {
        "error": {
            "code": "ROUND_NOT_FOUND",
            "message": "Round does not exist.",
            "details": {},
        }
    }
