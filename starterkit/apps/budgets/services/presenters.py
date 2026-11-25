from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser

from apps.budgets.domain import policies
from apps.budgets.domain.models import BudgetRequest
from apps.budgets.dto.budget_requests import BudgetRequestInputDTO
from apps.users.selectors.roles import Role


CENTS = Decimal("0.01")


def money(value: Decimal) -> str:
    return str(Decimal(value).quantize(CENTS))


def display_name(user: AbstractBaseUser | None) -> str | None:
    if user is None:
        return None
    return user.get_full_name() or user.get_username()


def request_props(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> dict:
    return {
        "id": request.pk,
        "title": request.title,
        "amount": str(request.amount),
        "justification": request.justification,
        "status": request.status,
        "status_label": request.get_status_display(),
        "requester": display_name(request.requester),
        "reviewer": display_name(request.reviewer),
        "review_note": request.review_note,
        "created_at": request.created_at.isoformat(),
        "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
        "can": {
            "edit": policies.can_edit(actor, role, request),
            "withdraw": policies.can_withdraw(actor, role, request),
            "review": policies.can_review(role, request),
            "delete": policies.can_delete(role),
        },
    }


def empty_form() -> dict:
    return {"title": "", "amount": "", "justification": ""}


def form_from_request(request: BudgetRequest) -> dict:
    return {"title": request.title, "amount": str(request.amount), "justification": request.justification}


def form_from_input(data: BudgetRequestInputDTO) -> dict:
    return {"title": data.title, "amount": data.amount, "justification": data.justification}
