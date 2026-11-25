from apps.users.domain.roles import Role, UserLike


def can_access_workspace(role: Role | None) -> bool:
    return role is not None


def can_assign_roles(actor: UserLike) -> bool:
    return bool(actor.is_authenticated and actor.is_active and actor.is_superuser)


def has_fixed_role(target: UserLike) -> bool:
    return bool(target.is_superuser)
