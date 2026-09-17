from django.contrib.auth.models import AbstractBaseUser

from apps.admin_panel.domain import policies
from apps.admin_panel.selectors import auth as auth_selectors
from apps.admin_panel.selectors import users as user_selectors
from apps.admin_panel.services.common import ensure_allowed

RECENT_USERS_LIMIT = 5


def get_dashboard_page(*, actor: AbstractBaseUser) -> dict:
    ensure_allowed(policies.can_access_admin(actor))

    can_view_users = policies.can_view_users(actor)
    can_view_groups = policies.can_view_groups(actor)
    return {
        "user_stats": auth_selectors.user_counts() if can_view_users else None,
        "group_stats": _group_stats() if can_view_groups else None,
        "recent_users": _recent_users(actor) if can_view_users else [],
        "can": {
            "view_users": can_view_users,
            "view_groups": can_view_groups,
            "add_users": policies.can_add_users(actor),
            "add_groups": policies.can_add_groups(actor),
        },
    }


def _group_stats() -> dict[str, int]:
    return {
        "total": auth_selectors.count_groups(),
        "permission_assignments": auth_selectors.count_group_permission_assignments(),
    }


def _recent_users(actor: AbstractBaseUser) -> list[dict]:
    return [
        {
            "id": user.pk,
            "username": user.username,
            "email": user.email or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat(),
            "can_edit": policies.can_change_user(actor, user),
        }
        for user in user_selectors.recent_users(limit=RECENT_USERS_LIMIT)
    ]
