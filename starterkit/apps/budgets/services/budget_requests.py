from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.http import Http404
from django.utils import timezone

from apps.budgets.domain import policies
from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.dto.budget_requests import (
    BudgetRequestInputDTO,
    BudgetRequestResultDTO,
    ReviewInputDTO,
)
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services import client_pages, manager_pages, presenters
from apps.budgets.services.validation import clean_request_input, clean_review_input
from apps.users.selectors.roles import role_for_user
from shared.services import ensure_allowed

ALREADY_REVIEWED_ERROR = "This request has already been reviewed and can no longer be changed."
NOT_PENDING_ERROR = "This request is no longer pending."


def create_request(*, actor: AbstractBaseUser, data: BudgetRequestInputDTO) -> BudgetRequestResultDTO:
    ensure_allowed(policies.can_create(role_for_user(actor)))

    clean, errors = clean_request_input(data)
    if errors:
        props = client_pages.create_form_props(form=presenters.form_from_input(data), errors=errors)
        return _failure(errors, page_props=props)

    request = BudgetRequest.objects.create(
        requester=actor, title=clean.title, amount=clean.amount, justification=clean.justification
    )
    return _success(request, f'Request "{request.title}" was submitted.')


def update_request(
    *, actor: AbstractBaseUser, request_id: int, data: BudgetRequestInputDTO
) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    clean, errors = clean_request_input(data)

    with transaction.atomic():
        request = _get_visible_for_update(actor, role, request_id)
        _ensure_owner_may_change(actor, role, request)
        if not request.is_pending:
            errors = {"non_field_errors": [ALREADY_REVIEWED_ERROR]}
        if errors:
            props = client_pages.edit_form_props(request, form=presenters.form_from_input(data), errors=errors)
            return _failure(errors, request_id, page_props=props)

        request.title = clean.title
        request.amount = clean.amount
        request.justification = clean.justification
        request.save(update_fields=["title", "amount", "justification", "updated_at"])
    return _success(request, f'Request "{request.title}" was updated.')


def withdraw_request(*, actor: AbstractBaseUser, request_id: int) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    with transaction.atomic():
        request = _get_visible_for_update(actor, role, request_id)
        _ensure_owner_may_change(actor, role, request)
        if not request.is_pending:
            return _failure({"non_field_errors": [ALREADY_REVIEWED_ERROR]}, request_id)

        request.status = Status.WITHDRAWN
        request.save(update_fields=["status", "updated_at"])
    return _success(request, f'Request "{request.title}" was withdrawn.')


def review_request(
    *, actor: AbstractBaseUser, request_id: int, data: ReviewInputDTO
) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    ensure_allowed(policies.can_view_review_queue(role))
    clean, errors = clean_review_input(data)

    with transaction.atomic():
        request = _get_for_update_or_404(request_id)
        if not policies.can_review(role, request):
            errors = {"non_field_errors": [NOT_PENDING_ERROR]}
        if errors:
            form = {"decision": data.decision, "note": data.note}
            props = manager_pages.review_page_props(actor, role, request, form=form, errors=errors)
            return _failure(errors, request_id, page_props=props)

        request.status = clean.status
        request.review_note = clean.note
        request.reviewer = actor
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "review_note", "reviewer", "reviewed_at", "updated_at"])
    return _success(request, f'Request "{request.title}" was {request.get_status_display().lower()}.')


def delete_request(*, actor: AbstractBaseUser, request_id: int) -> BudgetRequestResultDTO:
    ensure_allowed(policies.can_delete(role_for_user(actor)))
    with transaction.atomic():
        request = _get_for_update_or_404(request_id)
        title = request.title
        request.delete()
    return _success(None, f'Request "{title}" was permanently deleted.')


def _get_for_update_or_404(request_id: int) -> BudgetRequest:
    request = selectors.budget_request_get_for_update(request_id)
    if request is None:
        raise Http404("Budget request not found.")
    return request


def _get_visible_for_update(actor, role, request_id: int) -> BudgetRequest:
    request = _get_for_update_or_404(request_id)
    if not policies.can_view(actor, role, request):
        raise Http404("Budget request not found.")
    return request


def _ensure_owner_may_change(actor, role, request: BudgetRequest) -> None:
    is_owning_client = policies.can_view_own_requests(role) and request.requester_id == actor.pk
    ensure_allowed(is_owning_client)


def _success(request: BudgetRequest | None, message: str) -> BudgetRequestResultDTO:
    return BudgetRequestResultDTO(
        success=True, request_id=request.pk if request else None, message=message, errors={}
    )


def _failure(errors: dict, request_id: int | None = None, *, page_props: dict | None = None) -> BudgetRequestResultDTO:
    return BudgetRequestResultDTO(
        success=False, request_id=request_id, message="", errors=errors, page_props=page_props
    )
