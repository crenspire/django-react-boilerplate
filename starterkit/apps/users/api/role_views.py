from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render

from apps.users.dto.roles import AssignRoleInputDTO
from apps.users.services import roles as role_services
from shared.request_utils import get_request_data, parse_str


@require_http_methods(["GET", "POST"])
@login_required
def user_role(request: HttpRequest, user_id: int):
    if request.method == "GET":
        props = role_services.get_role_page(actor=request.user, user_id=user_id)
        return render(request, "Admin/Users/Role", props)

    data = AssignRoleInputDTO(user_id=user_id, role=parse_str(get_request_data(request).get("role")))
    result = role_services.assign_role(actor=request.user, data=data)
    if not result.success:
        return render(request, "Admin/Users/Role", result.page_props)
    messages.success(request, result.message)
    return redirect("admin_users")
