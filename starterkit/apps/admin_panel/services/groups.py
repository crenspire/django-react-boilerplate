from dataclasses import asdict

from django.contrib.auth.models import AbstractBaseUser, Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404

from apps.admin_panel.domain import policies
from apps.admin_panel.dto.common import DeleteResultDTO, ListQueryDTO
from apps.admin_panel.dto.groups import GroupFormInputDTO, GroupFormResultDTO, GroupListItemDTO
from apps.admin_panel.selectors import groups as group_selectors
from apps.admin_panel.services.common import (
    ensure_allowed,
    merge_errors,
    paginate,
    validation_errors,
)

ALLOWED_ORDER_FIELDS = frozenset(
    {
        "name", "-name",
        "user_count", "-user_count",
        "permission_count", "-permission_count",
    }
)
DEFAULT_ORDER = "name"
DUPLICATE_NAME_ERROR = "A group with that name already exists."


# Pages


def get_group_list_page(*, actor: AbstractBaseUser, query: ListQueryDTO) -> dict:
    ensure_allowed(policies.can_view_groups(actor))

    order_by = query.order_by if query.order_by in ALLOWED_ORDER_FIELDS else DEFAULT_ORDER
    queryset = group_selectors.group_list(search=query.search, order_by=order_by)
    page, pagination = paginate(queryset, page=query.page, page_size=query.page_size)

    can_edit = policies.can_change_groups(actor)
    can_delete = policies.can_delete_groups(actor)
    items = [
        GroupListItemDTO(
            id=group.pk,
            name=group.name,
            user_count=group.user_count,
            permission_count=group.permission_count,
            can_edit=can_edit,
            can_delete=can_delete,
        )
        for group in page
    ]
    return {
        "groups": [asdict(item) for item in items],
        "pagination": pagination,
        "filters": {"search": query.search, "order_by": order_by},
        "can": {"add": policies.can_add_groups(actor)},
    }


def get_group_create_page(*, actor: AbstractBaseUser) -> dict:
    ensure_allowed(policies.can_add_groups(actor))
    return _form_page_props(actor, form={"name": "", "permission_ids": []}, errors={})


def get_group_edit_page(*, actor: AbstractBaseUser, group_id: int) -> dict:
    ensure_allowed(policies.can_change_groups(actor))
    group = _get_group_or_404(group_id)
    form = {
        "name": group.name,
        "permission_ids": sorted(group_selectors.group_permission_ids(group)),
    }
    return _edit_page_props(
        actor, header={"id": group.pk, "name": group.name}, form=form, errors={}
    )


# Mutations


def create_group(*, actor: AbstractBaseUser, data: GroupFormInputDTO) -> GroupFormResultDTO:
    ensure_allowed(policies.can_add_groups(actor))

    group = Group(name=data.name.strip())
    permission_ids = frozenset(data.permission_ids)

    errors = merge_errors(
        _permission_assignment_errors(actor, permission_ids, current=frozenset()),
        _model_errors(group),
    )
    if not errors:
        try:
            with transaction.atomic():
                group.save()
                group.permissions.set(group_selectors.permissions_by_ids(permission_ids))
        except IntegrityError:
            errors = {"name": [DUPLICATE_NAME_ERROR]}

    if errors:
        return GroupFormResultDTO(
            success=False,
            group_id=None,
            message="",
            errors=errors,
            page_props=_form_page_props(actor, form=_form_from_input(data), errors=errors),
        )
    return GroupFormResultDTO(
        success=True,
        group_id=group.pk,
        message=f'Group "{group.name}" was created.',
        errors={},
        page_props=None,
    )


def update_group(
    *,
    actor: AbstractBaseUser,
    group_id: int,
    data: GroupFormInputDTO,
) -> GroupFormResultDTO:
    ensure_allowed(policies.can_change_groups(actor))
    group = _get_group_or_404(group_id)

    header = {"id": group.pk, "name": group.name}
    current_permission_ids = frozenset(group_selectors.group_permission_ids(group))
    permission_ids = frozenset(data.permission_ids)
    group.name = data.name.strip()

    errors = merge_errors(
        _permission_assignment_errors(actor, permission_ids, current=current_permission_ids),
        _model_errors(group),
    )
    if not errors:
        try:
            with transaction.atomic():
                group.save()
                group.permissions.set(group_selectors.permissions_by_ids(permission_ids))
        except IntegrityError:
            errors = {"name": [DUPLICATE_NAME_ERROR]}

    if errors:
        return GroupFormResultDTO(
            success=False,
            group_id=group_id,
            message="",
            errors=errors,
            page_props=_edit_page_props(
                actor, header=header, form=_form_from_input(data), errors=errors
            ),
        )
    return GroupFormResultDTO(
        success=True,
        group_id=group.pk,
        message=f'Group "{group.name}" was updated.',
        errors={},
        page_props=None,
    )


def delete_group(*, actor: AbstractBaseUser, group_id: int) -> DeleteResultDTO:
    ensure_allowed(policies.can_delete_groups(actor))
    group = _get_group_or_404(group_id)
    name = group.name
    group.delete()
    return DeleteResultDTO(success=True, message=f'Group "{name}" was deleted.')


# Helpers


def _get_group_or_404(group_id: int) -> Group:
    group = group_selectors.group_get(group_id)
    if group is None:
        raise Http404("Group not found.")
    return group


def _permission_assignment_errors(
    actor: AbstractBaseUser,
    permission_ids: frozenset[int],
    *,
    current: frozenset[int],
) -> dict[str, list[str]]:
    if permission_ids == current or policies.can_assign_permissions(actor):
        return {}
    return {"permission_ids": ["Only superusers can change group permissions."]}


def _model_errors(group: Group) -> dict[str, list[str]]:
    try:
        group.full_clean()
    except ValidationError as exc:
        return validation_errors(exc)
    return {}


def _form_from_input(data: GroupFormInputDTO) -> dict:
    return {"name": data.name, "permission_ids": sorted(frozenset(data.permission_ids))}


def _form_page_props(actor: AbstractBaseUser, *, form: dict, errors: dict) -> dict:
    return {
        "form": form,
        "errors": errors,
        "permissions_choices": [
            {"id": permission.pk, "codename": f"{permission.content_type.app_label}.{permission.codename}"}
            for permission in group_selectors.permission_choices()
        ],
        "can": {"assign_permissions": policies.can_assign_permissions(actor)},
    }


def _edit_page_props(actor: AbstractBaseUser, *, header: dict, form: dict, errors: dict) -> dict:
    props = _form_page_props(actor, form=form, errors=errors)
    props["group"] = header
    props["can"]["delete"] = policies.can_delete_groups(actor)
    return props
