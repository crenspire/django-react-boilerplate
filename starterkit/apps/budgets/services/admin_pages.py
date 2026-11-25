from django.contrib.auth.models import AbstractBaseUser

from apps.budgets.domain import policies
from apps.budgets.domain.models import Status
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services import presenters
from apps.users.selectors.roles import role_for_user
from shared.dto import ListQueryDTO
from shared.services import ensure_allowed, paginate


def get_overview_page(*, actor: AbstractBaseUser, query: ListQueryDTO, status: str) -> dict:
    role = role_for_user(actor)
    ensure_allowed(policies.can_view_all_requests(role))

    status = status if status in Status.values else ""
    page, pagination = paginate(selectors.all_requests(status=status), page=query.page, page_size=query.page_size)
    return {
        "summary": summary(selectors.totals()),
        "status": status,
        "statuses": [{"value": value, "label": label} for value, label in Status.choices],
        "requests": [presenters.request_props(actor, role, request) for request in page],
        "pagination": pagination,
    }


def summary(totals: dict) -> dict:
    result = {}
    for status in Status:
        key = status.value.lower()
        result[key] = {
            "label": status.label,
            "count": totals[f"{key}_count"],
            "amount": presenters.money(totals[f"{key}_amount"]),
        }
    result["total"] = {
        "label": "All requests",
        "count": sum(item["count"] for item in result.values()),
        "amount": presenters.money(sum(totals[f"{status.value.lower()}_amount"] for status in Status)),
    }
    return result
