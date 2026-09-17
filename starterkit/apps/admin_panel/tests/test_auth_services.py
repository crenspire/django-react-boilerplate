from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from apps.admin_panel.dto.auth import LoginInputDTO
from apps.admin_panel.services.auth import (
    INVALID_CREDENTIALS_ERROR,
    TOO_MANY_ATTEMPTS_ERROR,
    login_user,
    logout_user,
)
from apps.admin_panel.tests.factories import STRONG_PASSWORD, make_staff, make_user


def request_with_session():
    request = RequestFactory().post("/admin/login/")
    request.session = SessionStore()
    return request


def login_input(**overrides) -> LoginInputDTO:
    values = {
        "username": "staffuser",
        "password": STRONG_PASSWORD,
        "next_url": "",
        "default_redirect_url": "/admin/",
        "client_ip": "203.0.113.5",
    }
    values.update(overrides)
    return LoginInputDTO(**values)


class LoginServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_staff("staffuser")

    def test_login_success_redirects_to_default(self):
        request = request_with_session()
        result = login_user(request, login_input())
        self.assertTrue(result.success)
        self.assertEqual(result.redirect_url, "/admin/")
        self.assertEqual(request.session["_auth_user_id"], str(self.user.pk))

    def test_login_honours_safe_next_url(self):
        result = login_user(request_with_session(), login_input(next_url="/admin/users/"))
        self.assertEqual(result.redirect_url, "/admin/users/")

    def test_login_ignores_external_next_url(self):
        result = login_user(request_with_session(), login_input(next_url="https://evil.example/"))
        self.assertEqual(result.redirect_url, "/admin/")

    def test_wrong_password_returns_generic_error(self):
        result = login_user(request_with_session(), login_input(password="wrong"))
        self.assertFalse(result.success)
        self.assertEqual(result.errors, {"non_field_errors": [INVALID_CREDENTIALS_ERROR]})
        self.assertEqual(result.page_props["form"]["password"], "")

    def test_inactive_account_is_not_disclosed(self):
        make_user("ghost", is_staff=True, is_active=False)
        wrong = login_user(request_with_session(), login_input(username="ghost", password="wrong"))
        right = login_user(request_with_session(), login_input(username="ghost"))
        self.assertEqual(wrong.errors, {"non_field_errors": [INVALID_CREDENTIALS_ERROR]})
        self.assertEqual(right.errors, wrong.errors)

    def test_non_staff_cannot_log_in(self):
        make_user("regular")
        result = login_user(request_with_session(), login_input(username="regular"))
        self.assertEqual(result.errors, {"non_field_errors": [INVALID_CREDENTIALS_ERROR]})

    def test_empty_fields_return_validation_errors(self):
        result = login_user(request_with_session(), login_input(username="", password=""))
        self.assertEqual(set(result.errors), {"username", "password"})

    @override_settings(ADMIN_LOGIN_MAX_ATTEMPTS=3)
    def test_repeated_failures_are_throttled(self):
        for _ in range(3):
            login_user(request_with_session(), login_input(password="wrong"))

        result = login_user(request_with_session(), login_input())

        self.assertFalse(result.success)
        self.assertEqual(result.errors, {"non_field_errors": [TOO_MANY_ATTEMPTS_ERROR]})

    @override_settings(ADMIN_LOGIN_MAX_ATTEMPTS=3)
    def test_throttle_is_per_client(self):
        for _ in range(3):
            login_user(request_with_session(), login_input(password="wrong"))

        result = login_user(request_with_session(), login_input(client_ip="198.51.100.7"))

        self.assertTrue(result.success)

    @override_settings(ADMIN_LOGIN_MAX_ATTEMPTS=3)
    def test_successful_login_resets_counter(self):
        login_user(request_with_session(), login_input(password="wrong"))
        login_user(request_with_session(), login_input(password="wrong"))
        login_user(request_with_session(), login_input())
        login_user(request_with_session(), login_input(password="wrong"))

        result = login_user(request_with_session(), login_input())

        self.assertTrue(result.success)


class LogoutServiceTests(TestCase):
    def test_logout_clears_session_user(self):
        user = make_staff()
        request = request_with_session()
        request.user = user
        request.session["_auth_user_id"] = str(user.pk)

        logout_user(request)

        self.assertFalse(request.user.is_authenticated)
