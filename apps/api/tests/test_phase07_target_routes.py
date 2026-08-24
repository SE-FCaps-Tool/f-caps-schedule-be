from app.main import create_app


def test_phase07_controlled_operation_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("post", "/api/v1/sessions/{sessionId}/actions/change-room"),
        ("post", "/api/v1/sessions/{sessionId}/actions/replace-reviewer"),
        ("post", "/api/v1/sessions/{sessionId}/actions/postpone"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
