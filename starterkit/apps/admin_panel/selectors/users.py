from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

User = get_user_model()


def user_list(*, search: str = "", order_by: str = "username") -> QuerySet:
    qs = User.objects.order_by(order_by, "pk")
    term = search.strip()
    if term:
        qs = qs.filter(Q(username__icontains=term) | Q(email__icontains=term))
    return qs


def user_get(user_id: int) -> User | None:
    return User.objects.filter(pk=user_id).first()


def user_group_ids(user: User) -> list[int]:
    return list(user.groups.order_by("name").values_list("pk", flat=True))


def recent_users(*, limit: int) -> QuerySet:
    return User.objects.order_by("-date_joined", "-pk")[:limit]
