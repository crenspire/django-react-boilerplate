from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from inertia import render

from apps.admin_panel.api.request_utils import (
    get_request_data,
    parse_bool,
    parse_id_list,
    parse_list_query,
    parse_str,
)
from apps.admin_panel.dto.users import UserFormInputDTO
from apps.admin_panel.services import users as user_services


def _parse_user_form(request: HttpRequest) -> UserFormInputDTO:
    data = get_request_data(request)
    return UserFormInputDTO(
        username=parse_str(data.get("username")),
        email=parse_str(data.get("email")),
        first_name=parse_str(data.get("first_name")),
        last_name=parse_str(data.get("last_name")),
        is_staff=parse_bool(data.get("is_staff")),
        is_superuser=parse_bool(data.get("is_superuser")),
        is_active=parse_bool(data.get("is_active")),
        group_ids=parse_id_list(data.get("group_ids")),
        password=parse_str(data.get("password")),
    )


@require_GET
@login_required
def user_list(request: HttpRequest):
    props = user_services.get_user_list_page(actor=request.user, query=parse_list_query(request))
    return render(request, "Admin/Users/Index", props)


@require_http_methods(["GET", "POST"])
@login_required
def user_create(request: HttpRequest):
    if request.method == "GET":
        return render(request, "Admin/Users/Create", user_services.get_user_create_page(actor=request.user))

    result = user_services.create_user(actor=request.user, data=_parse_user_form(request))
    if not result.success:
        return render(request, "Admin/Users/Create", result.page_props)
    messages.success(request, result.message)
    return redirect("admin_user_edit", user_id=result.user_id)


@require_http_methods(["GET", "POST"])
@login_required
def user_edit(request: HttpRequest, user_id: int):
    if request.method == "GET":
        props = user_services.get_user_edit_page(actor=request.user, user_id=user_id)
        return render(request, "Admin/Users/Edit", props)

    result = user_services.update_user(
        actor=request.user, user_id=user_id, data=_parse_user_form(request)
    )
    if not result.success:
        return render(request, "Admin/Users/Edit", result.page_props)
    messages.success(request, result.message)
    return redirect("admin_user_edit", user_id=user_id)


@require_POST
@login_required
def user_delete(request: HttpRequest, user_id: int):
    result = user_services.delete_user(actor=request.user, user_id=user_id)
    add_message = messages.success if result.success else messages.error
    add_message(request, result.message)
    return redirect("admin_users")
