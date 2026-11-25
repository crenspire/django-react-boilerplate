from django.contrib.auth import get_user_model

from apps.users.domain.models import UserProfile

User = get_user_model()

STRONG_PASSWORD = "c0rrect-Horse-battery"


def make_user(username: str, *, role: str | None = None, **fields):
    user = User.objects.create_user(username=username, password=STRONG_PASSWORD, **fields)
    if role is not None:
        UserProfile.objects.create(user=user, role=role)
    return user


def make_superuser(username: str = "root", **fields):
    return make_user(username, is_staff=True, is_superuser=True, **fields)
