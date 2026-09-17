import hashlib

from django.conf import settings
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme

from apps.admin_panel.domain.policies import can_access_admin
from apps.admin_panel.dto.auth import LoginInputDTO, LoginResultDTO
from apps.admin_panel.infrastructure import attempt_counter

INVALID_CREDENTIALS_ERROR = (
    "Please enter the correct username and password for a staff account. "
    "Note that both fields may be case-sensitive."
)
TOO_MANY_ATTEMPTS_ERROR = "Too many failed login attempts. Please try again later."

# Login and logout are the only services that take the request: Django's
# session-based login/logout functions need it.


def get_login_page(*, next_url: str) -> dict:
    return _page_props(username="", next_url=next_url, errors={})


def login_user(request: HttpRequest, data: LoginInputDTO) -> LoginResultDTO:
    """
    Log in an active staff user, mirroring Django admin.

    The error message is identical for unknown users, wrong passwords, inactive
    accounts and non-staff accounts so the form cannot be used to probe accounts.
    Repeated failures from one client are throttled.
    """

    username = data.username.strip()
    user_key, client_key = _attempt_keys(username, data.client_ip)

    if _is_throttled(user_key, client_key):
        return _failure(username, data, {"non_field_errors": [TOO_MANY_ATTEMPTS_ERROR]})

    errors: dict[str, list[str]] = {}
    if not username:
        errors["username"] = ["This field is required."]
    if not data.password:
        errors["password"] = ["This field is required."]
    if errors:
        return _failure(username, data, errors)

    user = authenticate(request, username=username, password=data.password)
    if user is None or not can_access_admin(user):
        window = settings.ADMIN_LOGIN_LOCKOUT_SECONDS
        attempt_counter.increment(user_key, window_seconds=window)
        attempt_counter.increment(client_key, window_seconds=window)
        return _failure(username, data, {"non_field_errors": [INVALID_CREDENTIALS_ERROR]})

    attempt_counter.reset(user_key)
    django_login(request, user)

    return LoginResultDTO(
        success=True,
        redirect_url=_safe_redirect_url(request, data.next_url, data.default_redirect_url),
        errors={},
        page_props=None,
    )


def logout_user(request: HttpRequest) -> None:
    django_logout(request)


def _attempt_keys(username: str, client_ip: str) -> tuple[str, str]:
    # Hash user-supplied values so keys are always valid for any cache backend.
    user_digest = hashlib.sha256(f"{username.lower()}|{client_ip}".encode()).hexdigest()
    client_digest = hashlib.sha256(client_ip.encode()).hexdigest()
    return f"admin-login:user:{user_digest}", f"admin-login:client:{client_digest}"


def _is_throttled(user_key: str, client_key: str) -> bool:
    max_attempts = settings.ADMIN_LOGIN_MAX_ATTEMPTS
    # A single client may try a few usernames before being blocked outright.
    return (
        attempt_counter.get_count(user_key) >= max_attempts
        or attempt_counter.get_count(client_key) >= max_attempts * 4
    )


def _safe_redirect_url(request: HttpRequest, next_url: str, default_url: str) -> str:
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default_url


def _failure(username: str, data: LoginInputDTO, errors: dict) -> LoginResultDTO:
    return LoginResultDTO(
        success=False,
        redirect_url=None,
        errors=errors,
        page_props=_page_props(username=username, next_url=data.next_url, errors=errors),
    )


def _page_props(*, username: str, next_url: str, errors: dict) -> dict:
    # The password is never echoed back to the client.
    return {"form": {"username": username, "password": "", "next": next_url}, "errors": errors}
