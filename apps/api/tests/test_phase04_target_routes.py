from app.main import create_app


def test_phase04_target_round_registration_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/semesters/{semester_id}/rounds"),
        ("post", "/api/v1/semesters/{semester_id}/rounds"),
        ("get", "/api/v1/rounds/{round_id}/eligible-projects"),
        ("get", "/api/v1/rounds/{round_id}/registration-summary"),
        ("get", "/api/v1/rounds/{round_id}/scheduling-readiness"),
        ("post", "/api/v1/rounds/{round_id}/actions/open-registration"),
        ("post", "/api/v1/rounds/{round_id}/actions/close-registration"),
        ("get", "/api/v1/rounds/{round_id}/availability/me"),
        ("put", "/api/v1/rounds/{round_id}/availability/me"),
        ("post", "/api/v1/rounds/{round_id}/invitations/me/respond"),
        ("post", "/api/v1/rounds/{round_id}/invitations/{invitation_id}/remind"),
        ("get", "/api/v1/rounds/{round_id}/groups/{group_id}/preferences"),
        ("put", "/api/v1/rounds/{round_id}/groups/{group_id}/preferences"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
