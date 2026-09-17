"""
Permission rules for the Inertia admin.

Access mirrors Django admin: the user must be active staff, and every action
also needs the matching model permission (superusers implicitly have all).

On top of that, anything that grants privileges -- staff status, superuser
status, group membership and group permissions -- is reserved for superusers.
Without this rule a staff user holding `auth.change_user` could promote
themselves to superuser.
"""

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

UserLike = AbstractBaseUser | AnonymousUser


def can_access_admin(user: UserLike) -> bool:
    return bool(
        getattr(user, "is_authenticated", False)
        and getattr(user, "is_active", False)
        and getattr(user, "is_staff", False)
    )


def can_grant_privileges(user: UserLike) -> bool:
    """Only superusers may change staff/superuser flags, groups or group permissions."""
    return can_access_admin(user) and bool(getattr(user, "is_superuser", False))


def is_privileged_account(user: UserLike) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))


def _has_admin_perm(user: UserLike, perm: str) -> bool:
    return can_access_admin(user) and user.has_perm(perm)


# Users


def can_view_users(user: UserLike) -> bool:
    # Like Django admin, change permission implies view permission.
    return _has_admin_perm(user, "auth.view_user") or can_change_users(user)


def can_add_users(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.add_user")


def can_change_users(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.change_user")


def can_delete_users(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.delete_user")


def can_change_user(actor: UserLike, target: UserLike) -> bool:
    """Non-superusers may only edit accounts that carry no admin privileges."""
    if not can_change_users(actor):
        return False
    return can_grant_privileges(actor) or not is_privileged_account(target)


def can_delete_user(actor: UserLike, target: UserLike) -> bool:
    if not can_delete_users(actor):
        return False
    if actor.pk == target.pk:
        return False
    return can_grant_privileges(actor) or not is_privileged_account(target)


# Groups


def can_view_groups(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.view_group") or can_change_groups(user)


def can_add_groups(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.add_group")


def can_change_groups(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.change_group")


def can_delete_groups(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.delete_group")


def can_assign_permissions(user: UserLike) -> bool:
    return can_grant_privileges(user)
