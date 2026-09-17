from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

STRONG_PASSWORD = "c0rrect-Horse-battery"

USER_PERMS = ("view_user", "add_user", "change_user", "delete_user")
GROUP_PERMS = ("view_group", "add_group", "change_group", "delete_group")


def make_user(username: str, *, perms=(), password: str = STRONG_PASSWORD, **fields):
    user = User.objects.create_user(username=username, password=password, **fields)
    if perms:
        user.user_permissions.set(Permission.objects.filter(content_type__app_label="auth", codename__in=perms))
    # Re-fetch so the permission cache reflects the assigned permissions.
    return User.objects.get(pk=user.pk)


def make_staff(username: str = "staff", *, perms=(), **fields):
    return make_user(username, perms=perms, is_staff=True, **fields)


def make_superuser(username: str = "root", **fields):
    return make_user(username, is_staff=True, is_superuser=True, **fields)
