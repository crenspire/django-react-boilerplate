from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Count, DecimalField, Q, QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from apps.budgets.domain.models import BudgetRequest, Status


def _with_people() -> QuerySet:
    return BudgetRequest.objects.select_related("requester", "reviewer")


def budget_request_get(request_id: int) -> BudgetRequest | None:
    return _with_people().filter(pk=request_id).first()


def budget_request_get_for_update(request_id: int) -> BudgetRequest | None:
    return BudgetRequest.objects.select_for_update().filter(pk=request_id).first()


def requests_for_requester(requester: AbstractBaseUser) -> QuerySet:
    return _with_people().filter(requester=requester)


def request_exists_for(requester: AbstractBaseUser, title: str) -> bool:
    return BudgetRequest.objects.filter(requester=requester, title=title).exists()


def pending_requests() -> QuerySet:
    return _with_people().filter(status=Status.PENDING).order_by("created_at", "pk")


def decided_requests() -> QuerySet:
    return _with_people().filter(status__in=(Status.APPROVED, Status.REJECTED)).order_by(
        "-reviewed_at", "-pk"
    )


def all_requests(*, status: str = "") -> QuerySet:
    qs = _with_people()
    return qs.filter(status=status) if status else qs


def totals() -> dict:
    zero = Value(Decimal("0"), output_field=DecimalField(max_digits=14, decimal_places=2))
    aggregates = {}
    for status in Status:
        key = status.value.lower()
        match = Q(status=status)
        aggregates[f"{key}_count"] = Count("pk", filter=match)
        aggregates[f"{key}_amount"] = Coalesce(Sum("amount", filter=match), zero)
    return BudgetRequest.objects.aggregate(**aggregates)
