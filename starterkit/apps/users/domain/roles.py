from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import models

UserLike = AbstractBaseUser | AnonymousUser


class Role(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    MANAGER = "MANAGER", "Manager"
    ADMIN = "ADMIN", "Admin"


DEFAULT_ROLE = Role.CLIENT


def effective_role(user: UserLike, stored_role: str | None) -> Role | None:
    if not user.is_authenticated or not user.is_active:
        return None
    if user.is_superuser:
        return Role.ADMIN
    return DEFAULT_ROLE if stored_role is None else Role(stored_role)
