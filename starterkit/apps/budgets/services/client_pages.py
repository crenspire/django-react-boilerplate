from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.http import Http404

from apps.budgets.domain import policies
from apps.budgets.domain.models import BudgetRequest
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services import presenters
from apps.users.selectors.roles import role_for_user
from shared.dto import ListQueryDTO
from shared.services import ensure_allowed, paginate

LOCKED_MESSAGE = "This request has already been reviewed or withdrawn, so it can no longer be changed."


def get_my_requests_page(*, actor: AbstractBaseUser, query: ListQueryDTO) -> dict:
    role = role_for_user(actor)
    ensure_allowed(policies.can_view_own_requests(role))

    page, pagination = paginate(
        selectors.requests_for_requester(actor), page=query.page, page_size=query.page_size
    )
    return {
        "requests": [presenters.request_props(actor, role, request) for request in page],
        "pagination": pagination,
        "can": {"create": policies.can_create(role)},
    }


def get_create_page(*, actor: AbstractBaseUser) -> dict:
    ensure_allowed(policies.can_create(role_for_user(actor)))
    return create_form_props(form=presenters.empty_form(), errors={})


def get_edit_page(*, actor: AbstractBaseUser, request_id: int) -> dict:
    request = get_own_request(actor, request_id)
    return edit_form_props(request, form=presenters.form_from_request(request), errors={})


def get_own_request(actor: AbstractBaseUser, request_id: int) -> BudgetRequest:
    role = role_for_user(actor)
    request = selectors.budget_request_get(request_id)
    if request is None or not policies.can_view(actor, role, request):
        raise Http404("Budget request not found.")
    if request.requester_id != actor.pk or not policies.can_view_own_requests(role):
        raise PermissionDenied
    return request


def create_form_props(*, form: dict, errors: dict) -> dict:
    return {"form": form, "errors": errors}


def edit_form_props(request: BudgetRequest, *, form: dict, errors: dict) -> dict:
    editable = request.is_pending
    return {
        "request": {
            "id": request.pk,
            "title": request.title,
            "status": request.status,
            "status_label": request.get_status_display(),
        },
        "form": form,
        "errors": errors,
        "editable": editable,
        "locked_message": "" if editable else LOCKED_MESSAGE,
    }
