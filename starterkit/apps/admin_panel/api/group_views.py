from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from inertia import render

from apps.admin_panel.api.request_utils import (
    get_request_data,
    parse_id_list,
    parse_list_query,
    parse_str,
)
from apps.admin_panel.dto.groups import GroupFormInputDTO
from apps.admin_panel.services import groups as group_services


def _parse_group_form(request: HttpRequest) -> GroupFormInputDTO:
    data = get_request_data(request)
    return GroupFormInputDTO(
        name=parse_str(data.get("name")),
        permission_ids=parse_id_list(data.get("permission_ids")),
    )


@require_GET
@login_required
def group_list(request: HttpRequest):
    props = group_services.get_group_list_page(actor=request.user, query=parse_list_query(request))
    return render(request, "Admin/Groups/Index", props)


@require_http_methods(["GET", "POST"])
@login_required
def group_create(request: HttpRequest):
    if request.method == "GET":
        return render(request, "Admin/Groups/Create", group_services.get_group_create_page(actor=request.user))

    result = group_services.create_group(actor=request.user, data=_parse_group_form(request))
    if not result.success:
        return render(request, "Admin/Groups/Create", result.page_props)
    messages.success(request, result.message)
    return redirect("admin_group_edit", group_id=result.group_id)


@require_http_methods(["GET", "POST"])
@login_required
def group_edit(request: HttpRequest, group_id: int):
    if request.method == "GET":
        props = group_services.get_group_edit_page(actor=request.user, group_id=group_id)
        return render(request, "Admin/Groups/Edit", props)

    result = group_services.update_group(
        actor=request.user, group_id=group_id, data=_parse_group_form(request)
    )
    if not result.success:
        return render(request, "Admin/Groups/Edit", result.page_props)
    messages.success(request, result.message)
    return redirect("admin_group_edit", group_id=group_id)


@require_POST
@login_required
def group_delete(request: HttpRequest, group_id: int):
    result = group_services.delete_group(actor=request.user, group_id=group_id)
    messages.success(request, result.message)
    return redirect("admin_groups")
