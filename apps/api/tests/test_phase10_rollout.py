from app.api_contract import legacy_contract_headers


def test_legacy_contract_headers_identify_successor_and_sunset():
    headers = legacy_contract_headers("/api/v1/rounds/12/schedule/run")
    assert headers["Deprecation"] == "true"
    assert headers["Sunset"]
    assert "/api/v1/rounds/12/schedules/generate" in headers["Link"]


def test_target_routes_do_not_receive_legacy_headers():
    assert legacy_contract_headers("/api/v1/rounds/12/schedules/generate") == {}
