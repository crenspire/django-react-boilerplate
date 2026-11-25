from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from inertia import render

from apps.budgets.dto.budget_requests import BudgetRequestInputDTO
from apps.budgets.services import budget_requests as workflow
from apps.budgets.services import client_pages
from shared.request_utils import get_request_data, parse_list_query, parse_str


def _parse_request_form(request: HttpRequest) -> BudgetRequestInputDTO:
    data = get_request_data(request)
    amount = data.get("amount")
    return BudgetRequestInputDTO(
        title=parse_str(data.get("title")),
        amount=str(amount) if isinstance(amount, (int, float)) and not isinstance(amount, bool) else parse_str(amount),
        justification=parse_str(data.get("justification")),
    )


@require_GET
@login_required
def my_requests(request: HttpRequest):
    props = client_pages.get_my_requests_page(actor=request.user, query=parse_list_query(request))
    return render(request, "Budget/MyRequests/Index", props)


@require_http_methods(["GET", "POST"])
@login_required
def request_create(request: HttpRequest):
    if request.method == "GET":
        return render(request, "Budget/MyRequests/Create", client_pages.get_create_page(actor=request.user))

    result = workflow.create_request(actor=request.user, data=_parse_request_form(request))
    if not result.success:
        return render(request, "Budget/MyRequests/Create", result.page_props)
    messages.success(request, result.message)
    return redirect("budget_my_requests")


@require_http_methods(["GET", "POST"])
@login_required
def request_edit(request: HttpRequest, request_id: int):
    if request.method == "GET":
        props = client_pages.get_edit_page(actor=request.user, request_id=request_id)
        return render(request, "Budget/MyRequests/Edit", props)

    result = workflow.update_request(
        actor=request.user, request_id=request_id, data=_parse_request_form(request)
    )
    if not result.success:
        return render(request, "Budget/MyRequests/Edit", result.page_props)
    messages.success(request, result.message)
    return redirect("budget_my_requests")


@require_POST
@login_required
def request_withdraw(request: HttpRequest, request_id: int):
    result = workflow.withdraw_request(actor=request.user, request_id=request_id)
    add_message = messages.success if result.success else messages.error
    add_message(request, result.message or result.errors["non_field_errors"][0])
    return redirect("budget_my_requests")
