from app.main import create_app


def test_phase05_target_schedule_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/rounds/{round_id}/schedules"),
        ("post", "/api/v1/rounds/{round_id}/schedules/generate"),
        ("get", "/api/v1/rounds/{round_id}/schedules/{schedule_id}"),
        ("post", "/api/v1/rounds/{round_id}/schedules/{schedule_id}/actions/discard"),
        ("post", "/api/v1/rounds/{round_id}/schedules/{schedule_id}/actions/set-active"),
        ("get", "/api/v1/rounds/{round_id}/sessions"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
