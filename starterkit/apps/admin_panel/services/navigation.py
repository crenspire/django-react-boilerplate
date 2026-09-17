from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from apps.admin_panel.domain import policies


def get_admin_navigation(*, actor: AbstractBaseUser | AnonymousUser) -> list[dict]:
    """
    Sidebar entries the actor may open, grouped by `section`.

    Items reference Django route names; the frontend resolves them to URLs.
    """

    if not policies.can_access_admin(actor):
        return []

    items = [
        {"section": "Overview", "label": "Dashboard", "icon": "dashboard", "route": "admin_dashboard"},
    ]
    if policies.can_view_users(actor):
        items.append({"section": "Management", "label": "Users", "icon": "users", "route": "admin_users"})
    if policies.can_view_groups(actor):
        items.append({"section": "Management", "label": "Groups", "icon": "groups", "route": "admin_groups"})
    return items
