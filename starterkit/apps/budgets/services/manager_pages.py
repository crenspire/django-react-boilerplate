from django.contrib.auth.models import AbstractBaseUser
from django.http import Http404

from apps.budgets.domain import policies
from apps.budgets.domain.models import BudgetRequest
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services import presenters
from apps.users.selectors.roles import Role, role_for_user
from shared.dto import ListQueryDTO
from shared.services import ensure_allowed, paginate

PENDING_TAB = "pending"
HISTORY_TAB = "history"
TABS = (PENDING_TAB, HISTORY_TAB)


def get_review_queue_page(*, actor: AbstractBaseUser, query: ListQueryDTO, tab: str) -> dict:
    role = role_for_user(actor)
    ensure_allowed(policies.can_view_review_queue(role))

    tab = tab if tab in TABS else PENDING_TAB
    queryset = selectors.pending_requests() if tab == PENDING_TAB else selectors.decided_requests()
    page, pagination = paginate(queryset, page=query.page, page_size=query.page_size)
    totals = selectors.totals()
    return {
        "tab": tab,
        "requests": [presenters.request_props(actor, role, request) for request in page],
        "pagination": pagination,
        "counts": {
            "pending": totals["pending_count"],
            "history": totals["approved_count"] + totals["rejected_count"],
        },
        "pending_amount": presenters.money(totals["pending_amount"]),
    }


def get_review_page(*, actor: AbstractBaseUser, request_id: int) -> dict:
    role = role_for_user(actor)
    ensure_allowed(policies.can_view_review_queue(role))
    request = selectors.budget_request_get(request_id)
    if request is None:
        raise Http404("Budget request not found.")
    return review_page_props(actor, role, request, form=empty_review_form(), errors={})


def empty_review_form() -> dict:
    return {"decision": "", "note": ""}


def review_page_props(
    actor: AbstractBaseUser, role: Role | None, request: BudgetRequest, *, form: dict, errors: dict
) -> dict:
    return {
        "request": presenters.request_props(actor, role, request),
        "form": form,
        "errors": errors,
    }
