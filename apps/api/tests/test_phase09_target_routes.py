from app.main import create_app


def test_phase09_portal_target_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/lecturer/me/invitations"),
        ("get", "/api/v1/lecturer/me/remediations"),
        ("get", "/api/v1/lecturer/me/sessions"),
        ("get", "/api/v1/lecturer/me/supervised-projects"),
        ("get", "/api/v1/leader/me/dashboard"),
        ("get", "/api/v1/leader/me/sessions"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected
