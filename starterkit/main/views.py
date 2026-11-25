from django.http import HttpRequest
from inertia import render


def home(request: HttpRequest):
    """Landing page: hero, features, footer."""
    return render(request, "Home", {})


def permission_denied(request: HttpRequest, exception=None):
    return _error_page(
        request,
        status=403,
        title="Access denied",
        message="You do not have permission to view this page or perform this action.",
    )


def page_not_found(request: HttpRequest, exception=None):
    return _error_page(
        request,
        status=404,
        title="Page not found",
        message="The page you are looking for does not exist or is no longer available.",
    )


def _error_page(request: HttpRequest, *, status: int, title: str, message: str):
    response = render(request, "Error", {"status": status, "title": title, "message": message})
    response.status_code = status
    return response
