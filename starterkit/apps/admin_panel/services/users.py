from dataclasses import asdict, dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404

from apps.admin_panel.domain import policies
from apps.admin_panel.dto.common import DeleteResultDTO, ListQueryDTO
from apps.admin_panel.dto.users import UserFormInputDTO, UserFormResultDTO, UserListItemDTO
from apps.admin_panel.selectors import groups as group_selectors
from apps.admin_panel.selectors import users as user_selectors
from apps.admin_panel.services.common import (
    ensure_allowed,
    merge_errors,
    paginate,
    validation_errors,
)

User = get_user_model()

ALLOWED_ORDER_FIELDS = frozenset(
    {
        "username", "-username",
        "email", "-email",
        "is_staff", "-is_staff",
        "is_active", "-is_active",
        "is_superuser", "-is_superuser",
    }
)
DEFAULT_ORDER = "username"
DUPLICATE_USERNAME_ERROR = "A user with that username already exists."


# Pages


def get_user_list_page(*, actor: User, query: ListQueryDTO) -> dict:
    ensure_allowed(policies.can_view_users(actor))

    order_by = query.order_by if query.order_by in ALLOWED_ORDER_FIELDS else DEFAULT_ORDER
    queryset = user_selectors.user_list(search=query.search, order_by=order_by)
    page, pagination = paginate(queryset, page=query.page, page_size=query.page_size)

    return {
        "users": [asdict(_list_item(actor, user)) for user in page],
        "pagination": pagination,
        "filters": {"search": query.search, "order_by": order_by},
        "can": {"add": policies.can_add_users(actor)},
    }


def get_user_create_page(*, actor: User) -> dict:
    ensure_allowed(policies.can_add_users(actor))
    return _form_page_props(actor, form=_empty_form(), errors={})


def get_user_edit_page(*, actor: User, user_id: int) -> dict:
    ensure_allowed(policies.can_change_users(actor))
    user = _get_user_or_404(user_id)
    ensure_allowed(policies.can_change_user(actor, user))
    return _edit_page_props(
        actor,
        header={"id": user.pk, "username": user.username},
        form=_form_from_user(user),
        errors={},
    )


# Mutations


def create_user(*, actor: User, data: UserFormInputDTO) -> UserFormResultDTO:
    ensure_allowed(policies.can_add_users(actor))

    user = User()
    _apply_profile(user, data)
    group_ids = frozenset(data.group_ids)

    errors = merge_errors(
        _privilege_errors(actor, data, current=None),
        _model_errors(user),
        _password_errors(user, data.password, required=True),
    )
    if not errors:
        try:
            with transaction.atomic():
                user.set_password(data.password)
                user.save()
                user.groups.set(group_selectors.groups_by_ids(group_ids))
        except IntegrityError:
            errors = {"username": [DUPLICATE_USERNAME_ERROR]}

    if errors:
        return UserFormResultDTO(
            success=False,
            user_id=None,
            message="",
            errors=errors,
            page_props=_form_page_props(actor, form=_form_from_input(data), errors=errors),
        )
    return UserFormResultDTO(
        success=True,
        user_id=user.pk,
        message=f'User "{user.username}" was created.',
        errors={},
        page_props=None,
    )


def update_user(*, actor: User, user_id: int, data: UserFormInputDTO) -> UserFormResultDTO:
    ensure_allowed(policies.can_change_users(actor))
    user = _get_user_or_404(user_id)
    ensure_allowed(policies.can_change_user(actor, user))

    current = _CurrentPrivileges(
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        group_ids=frozenset(user_selectors.user_group_ids(user)),
    )
    # Page header shows the stored username, not the (possibly invalid) submitted one.
    header = {"id": user.pk, "username": user.username}

    _apply_profile(user, data)
    group_ids = frozenset(data.group_ids)

    errors = merge_errors(
        _privilege_errors(actor, data, current=current),
        _self_lockout_errors(actor, user, data),
        _model_errors(user),
        _password_errors(user, data.password, required=False),
    )
    if not errors:
        try:
            with transaction.atomic():
                if data.password:
                    user.set_password(data.password)
                user.save()
                user.groups.set(group_selectors.groups_by_ids(group_ids))
        except IntegrityError:
            errors = {"username": [DUPLICATE_USERNAME_ERROR]}

    if errors:
        return UserFormResultDTO(
            success=False,
            user_id=user_id,
            message="",
            errors=errors,
            page_props=_edit_page_props(
                actor, header=header, form=_form_from_input(data), errors=errors
            ),
        )
    return UserFormResultDTO(
        success=True,
        user_id=user.pk,
        message=f'User "{user.username}" was updated.',
        errors={},
        page_props=None,
    )


def delete_user(*, actor: User, user_id: int) -> DeleteResultDTO:
    ensure_allowed(policies.can_delete_users(actor))
    user = _get_user_or_404(user_id)

    if user.pk == actor.pk:
        return DeleteResultDTO(success=False, message="You cannot delete your own account.")
    if not policies.can_delete_user(actor, user):
        return DeleteResultDTO(
            success=False,
            message="Only superusers can delete staff or superuser accounts.",
        )

    username = user.username
    user.delete()
    return DeleteResultDTO(success=True, message=f'User "{username}" was deleted.')


# Helpers


@dataclass(frozen=True)
class _CurrentPrivileges:
    is_staff: bool
    is_superuser: bool
    group_ids: frozenset[int]


def _get_user_or_404(user_id: int) -> User:
    user = user_selectors.user_get(user_id)
    if user is None:
        raise Http404("User not found.")
    return user


def _apply_profile(user: User, data: UserFormInputDTO) -> None:
    user.username = data.username.strip()
    user.email = data.email.strip()
    user.first_name = data.first_name.strip()
    user.last_name = data.last_name.strip()
    user.is_active = data.is_active
    user.is_staff = data.is_staff
    user.is_superuser = data.is_superuser


def _privilege_errors(
    actor: User,
    data: UserFormInputDTO,
    *,
    current: _CurrentPrivileges | None,
) -> dict[str, list[str]]:
    """Reject privilege changes from users who may not grant privileges."""
    if policies.can_grant_privileges(actor):
        return {}

    current_staff = current.is_staff if current else False
    current_superuser = current.is_superuser if current else False
    current_groups = current.group_ids if current else frozenset()

    errors: dict[str, list[str]] = {}
    if data.is_staff != current_staff:
        errors["is_staff"] = ["Only superusers can change staff status."]
    if data.is_superuser != current_superuser:
        errors["is_superuser"] = ["Only superusers can change superuser status."]
    if frozenset(data.group_ids) != current_groups:
        errors["group_ids"] = ["Only superusers can change group membership."]
    return errors


def _self_lockout_errors(actor: User, user: User, data: UserFormInputDTO) -> dict[str, list[str]]:
    """Stop admins from removing their own access by accident."""
    if user.pk != actor.pk:
        return {}
    errors: dict[str, list[str]] = {}
    if not data.is_active:
        errors["is_active"] = ["You cannot deactivate your own account."]
    if not data.is_staff:
        errors["is_staff"] = ["You cannot remove your own staff status."]
    if actor.is_superuser and not data.is_superuser:
        errors["is_superuser"] = ["You cannot remove your own superuser status."]
    return errors


def _model_errors(user: User) -> dict[str, list[str]]:
    """Run the model's own validation (username format, uniqueness, email, lengths)."""
    try:
        user.full_clean(exclude=["password"])
    except ValidationError as exc:
        return validation_errors(exc)
    return {}


def _password_errors(user: User, password: str, *, required: bool) -> dict[str, list[str]]:
    if not password:
        return {"password": ["This field is required."]} if required else {}
    try:
        validate_password(password, user)
    except ValidationError as exc:
        return {"password": list(exc.messages)}
    return {}


def _list_item(actor: User, user: User) -> UserListItemDTO:
    return UserListItemDTO(
        id=user.pk,
        username=user.username,
        email=user.email or "",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        can_edit=policies.can_change_user(actor, user),
        can_delete=policies.can_delete_user(actor, user),
    )


def _empty_form() -> dict:
    return {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "group_ids": [],
        "password": "",
    }


def _form_from_user(user: User) -> dict:
    return {
        "username": user.username,
        "email": user.email or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "group_ids": user_selectors.user_group_ids(user),
        "password": "",
    }


def _form_from_input(data: UserFormInputDTO) -> dict:
    return {
        "username": data.username,
        "email": data.email,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "is_staff": data.is_staff,
        "is_superuser": data.is_superuser,
        "is_active": data.is_active,
        "group_ids": sorted(frozenset(data.group_ids)),
        # Never echo a password back to the client.
        "password": "",
    }


def _form_page_props(actor: User, *, form: dict, errors: dict) -> dict:
    return {
        "form": form,
        "errors": errors,
        "groups_choices": [
            {"id": group.pk, "name": group.name} for group in group_selectors.group_choices()
        ],
        "can": {"grant_privileges": policies.can_grant_privileges(actor)},
    }


def _edit_page_props(actor: User, *, header: dict, form: dict, errors: dict) -> dict:
    props = _form_page_props(actor, form=form, errors=errors)
    props["user"] = header
    props["can"]["delete"] = policies.can_delete_users(actor) and header["id"] != actor.pk
    return props
