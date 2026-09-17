from collections.abc import Iterable

from django.contrib.auth.models import Group, Permission
from django.db.models import Count, QuerySet


def group_list(*, search: str = "", order_by: str = "name") -> QuerySet:
    # distinct=True is required: two COUNTs over separate joins otherwise
    # multiply each other (3 users x 4 permissions would report 12 and 12).
    qs = Group.objects.annotate(
        user_count=Count("user", distinct=True),
        permission_count=Count("permissions", distinct=True),
    ).order_by(order_by, "pk")
    term = search.strip()
    if term:
        qs = qs.filter(name__icontains=term)
    return qs


def group_get(group_id: int) -> Group | None:
    return Group.objects.filter(pk=group_id).first()


def group_choices() -> QuerySet:
    return Group.objects.order_by("name")


def groups_by_ids(group_ids: Iterable[int]) -> QuerySet:
    return Group.objects.filter(pk__in=list(group_ids))


def group_permission_ids(group: Group) -> list[int]:
    return list(group.permissions.values_list("pk", flat=True))


def permission_choices() -> QuerySet:
    return Permission.objects.select_related("content_type").order_by(
        "content_type__app_label", "codename"
    )


def permissions_by_ids(permission_ids: Iterable[int]) -> QuerySet:
    return Permission.objects.filter(pk__in=list(permission_ids))
