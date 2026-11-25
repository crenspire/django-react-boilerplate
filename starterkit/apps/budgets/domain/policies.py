from django.contrib.auth.models import AbstractBaseUser

from apps.budgets.domain.models import BudgetRequest
from apps.users.selectors.roles import Role


def can_create(role: Role | None) -> bool:
    return role == Role.CLIENT


def can_view_own_requests(role: Role | None) -> bool:
    return role == Role.CLIENT


def can_view_review_queue(role: Role | None) -> bool:
    return role == Role.MANAGER


def can_view_all_requests(role: Role | None) -> bool:
    return role == Role.ADMIN


def _is_owner(actor: AbstractBaseUser, request: BudgetRequest) -> bool:
    return request.requester_id == actor.pk


def can_view(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    return role == Role.CLIENT and _is_owner(actor, request)


def can_edit(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    return role == Role.CLIENT and _is_owner(actor, request) and request.is_pending


def can_withdraw(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    return can_edit(actor, role, request)


def can_review(role: Role | None, request: BudgetRequest) -> bool:
    return role == Role.MANAGER and request.is_pending


def can_delete(role: Role | None) -> bool:
    return role == Role.ADMIN
