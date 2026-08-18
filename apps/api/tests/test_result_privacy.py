from app.auth import CurrentUser
from app.services.access import is_management_user


def test_management_scope_is_explicit():
    assert is_management_user(CurrentUser(role="MANAGER")) is True
    assert is_management_user(CurrentUser(role="LECTURER")) is False
