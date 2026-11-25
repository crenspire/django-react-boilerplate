from django.contrib.auth import get_user_model
from django.http import Http404

from apps.users.domain import policies
from apps.users.domain.models import UserProfile
from apps.users.domain.roles import DEFAULT_ROLE, Role
from apps.users.dto.roles import AssignRoleInputDTO, AssignRoleResultDTO
from apps.users.selectors import roles as role_selectors
from shared.services import ensure_allowed

User = get_user_model()

INVALID_ROLE_ERROR = "Select a valid role."
FIXED_ROLE_ERROR = "Superusers are always admins; their role cannot be changed."


def get_role_page(*, actor: User, user_id: int) -> dict:
    ensure_allowed(policies.can_assign_roles(actor))
    user = _get_user_or_404(user_id)
    return _page_props(user, role=_current_role(user), errors={})


def assign_role(*, actor: User, data: AssignRoleInputDTO) -> AssignRoleResultDTO:
    ensure_allowed(policies.can_assign_roles(actor))
    user = _get_user_or_404(data.user_id)

    if policies.has_fixed_role(user):
        return _failure(user, role=_current_role(user), error=FIXED_ROLE_ERROR)
    if data.role not in Role.values:
        return _failure(user, role=_current_role(user), error=INVALID_ROLE_ERROR)

    UserProfile.objects.update_or_create(user=user, defaults={"role": data.role})
    return AssignRoleResultDTO(
        success=True,
        message=f'"{user.get_username()}" now has the {Role(data.role).label} role.',
        errors={},
        page_props=None,
    )


def _get_user_or_404(user_id: int) -> User:
    user = role_selectors.user_get(user_id)
    if user is None:
        raise Http404("User not found.")
    return user


def _current_role(user: User) -> str:
    if policies.has_fixed_role(user):
        return Role.ADMIN.value
    return role_selectors.stored_role(user) or DEFAULT_ROLE.value


def _failure(user: User, *, role: str, error: str) -> AssignRoleResultDTO:
    errors = {"role": [error]}
    return AssignRoleResultDTO(
        success=False,
        message="",
        errors=errors,
        page_props=_page_props(user, role=role, errors=errors),
    )


def _page_props(user: User, *, role: str, errors: dict) -> dict:
    return {
        "user": {"id": user.pk, "username": user.get_username()},
        "form": {"role": role},
        "errors": errors,
        "role_choices": [{"value": choice.value, "label": choice.label} for choice in Role],
        "fixed_role_message": FIXED_ROLE_ERROR if policies.has_fixed_role(user) else "",
    }
