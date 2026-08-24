from app.main import create_app


def test_phase05_target_schedule_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/rounds/{roundId}/schedules"),
        ("post", "/api/v1/rounds/{roundId}/schedules/generate"),
        ("get", "/api/v1/rounds/{roundId}/schedules/{scheduleId}"),
        ("post", "/api/v1/rounds/{roundId}/schedules/{scheduleId}/actions/discard"),
        ("post", "/api/v1/rounds/{roundId}/schedules/{scheduleId}/actions/set-active"),
        ("get", "/api/v1/rounds/{roundId}/sessions"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
