from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from apps.budgets.domain import policies
from apps.users.selectors.roles import role_for_user


def get_budget_navigation(*, actor: AbstractBaseUser | AnonymousUser) -> list[dict]:
    role = role_for_user(actor)
    items = []
    if policies.can_view_own_requests(role):
        items.append({"section": "Budget", "label": "My requests", "icon": "requests", "route": "budget_my_requests"})
    if policies.can_create(role):
        items.append({"section": "Budget", "label": "New request", "icon": "new", "route": "budget_request_create"})
    if policies.can_view_review_queue(role):
        items.append({"section": "Budget", "label": "Review queue", "icon": "review", "route": "budget_review_queue"})
    if policies.can_view_all_requests(role):
        items.append({"section": "Budget", "label": "Overview", "icon": "overview", "route": "budget_overview"})
    return items
