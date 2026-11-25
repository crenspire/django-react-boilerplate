from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from apps.users.domain import policies
from apps.users.domain.roles import Role
from apps.users.selectors.roles import role_for_user
from shared.services import ensure_allowed

ROLE_DESCRIPTIONS = {
    Role.CLIENT: "Submit budget requests and track their decisions.",
    Role.MANAGER: "Review budget requests from across the organization.",
    Role.ADMIN: "Oversee every budget request and the organization's totals.",
}


def get_workspace_page(*, actor: AbstractBaseUser) -> dict:
    role = role_for_user(actor)
    ensure_allowed(policies.can_access_workspace(role))
    return {
        "display_name": actor.get_full_name() or actor.get_username(),
        "role": role.label,
        "description": ROLE_DESCRIPTIONS[role],
    }


def get_workspace_navigation(*, actor: AbstractBaseUser | AnonymousUser) -> list[dict]:
    if not policies.can_access_workspace(role_for_user(actor)):
        return []
    return [{"section": "Workspace", "label": "Home", "icon": "home", "route": "workspace"}]
