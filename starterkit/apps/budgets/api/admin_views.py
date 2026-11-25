from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from inertia import render

from apps.budgets.services import admin_pages
from apps.budgets.services import budget_requests as workflow
from shared.request_utils import get_request_data, parse_list_query, parse_str


@require_GET
@login_required
def overview(request: HttpRequest):
    props = admin_pages.get_overview_page(
        actor=request.user, query=parse_list_query(request), status=request.GET.get("status", "")
    )
    return render(request, "Budget/Overview/Index", props)


@require_POST
@login_required
def request_delete(request: HttpRequest, request_id: int):
    result = workflow.delete_request(actor=request.user, request_id=request_id)
    messages.success(request, result.message)
    status = parse_str(get_request_data(request).get("status"))
    query = f"?{urlencode({'status': status})}" if status else ""
    return redirect(f"{reverse('budget_overview')}{query}")
