from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from inertia import render

from apps.budgets.dto.budget_requests import ReviewInputDTO
from apps.budgets.services import budget_requests as workflow
from apps.budgets.services import manager_pages
from shared.request_utils import get_request_data, parse_list_query, parse_str


@require_GET
@login_required
def review_queue(request: HttpRequest):
    props = manager_pages.get_review_queue_page(
        actor=request.user, query=parse_list_query(request), tab=request.GET.get("tab", "")
    )
    return render(request, "Budget/Review/Index", props)


@require_http_methods(["GET", "POST"])
@login_required
def review(request: HttpRequest, request_id: int):
    if request.method == "GET":
        props = manager_pages.get_review_page(actor=request.user, request_id=request_id)
        return render(request, "Budget/Review/Show", props)

    data = get_request_data(request)
    result = workflow.review_request(
        actor=request.user,
        request_id=request_id,
        data=ReviewInputDTO(decision=parse_str(data.get("decision")), note=parse_str(data.get("note"))),
    )
    if not result.success:
        return render(request, "Budget/Review/Show", result.page_props)
    messages.success(request, result.message)
    return redirect(f"{reverse('budget_review_queue')}?tab={parse_str(data.get('tab')) or 'pending'}")
