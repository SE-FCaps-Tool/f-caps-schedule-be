from app.main import create_app


def test_phase06_room_and_publish_target_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/rooms"),
        ("post", "/api/v1/rooms"),
        ("patch", "/api/v1/rooms/{room_id}"),
        ("get", "/api/v1/rounds/{round_id}/publish-readiness"),
        ("post", "/api/v1/rounds/{round_id}/actions/publish"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
