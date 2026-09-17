from django.contrib import messages
from django.middleware.csrf import get_token
from inertia import share

from apps.admin_panel.services.navigation import get_admin_navigation
from main.routes import route_map


def get_auth_props(request) -> dict:
    """
    Authenticated user shown in the UI. Permission flags are deliberately not
    included: the backend decides what each page may show.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"user": None}
    return {
        "user": {
            "id": user.pk,
            "username": user.get_username(),
            "email": getattr(user, "email", "") or "",
            "first_name": getattr(user, "first_name", "") or "",
            "last_name": getattr(user, "last_name", "") or "",
        }
    }


def get_flash_props(request) -> list[dict]:
    return [
        {"level": message.level_tag, "message": str(message)}
        for message in messages.get_messages(request)
    ]


def inertia_shared_props(get_response):
    """
    Share global Inertia props, keeping Django authoritative.

    Values are callables so they are only evaluated when a page is rendered:
    flash messages added by a view in the same request are included, and
    redirects do not consume them.
    """

    def middleware(request):
        # Mark the CSRF token as used so CsrfViewMiddleware sets the csrftoken
        # cookie that frontend/app.jsx sends back as X-CSRFToken. (Inertia's own
        # middleware calls get_token too late, outside CsrfViewMiddleware.)
        get_token(request)
        share(
            request,
            auth=lambda: get_auth_props(request),
            flash=lambda: get_flash_props(request),
            routes=route_map,
            admin_nav=lambda: get_admin_navigation(actor=request.user),
        )
        return get_response(request)

    return middleware
