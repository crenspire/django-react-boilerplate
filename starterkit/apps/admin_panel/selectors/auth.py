from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Count, Q

User = get_user_model()


def user_counts() -> dict[str, int]:
    return User.objects.aggregate(
        total=Count("pk"),
        active=Count("pk", filter=Q(is_active=True)),
        staff=Count("pk", filter=Q(is_staff=True)),
        superusers=Count("pk", filter=Q(is_superuser=True)),
    )


def count_groups() -> int:
    return Group.objects.count()


def count_group_permission_assignments() -> int:
    return Permission.objects.filter(group__isnull=False).count()
