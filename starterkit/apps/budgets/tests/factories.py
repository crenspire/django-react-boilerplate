from decimal import Decimal

from django.utils import timezone

from apps.budgets.domain.models import REVIEW_OUTCOMES, BudgetRequest, Status
from apps.users.tests.factories import make_superuser, make_user  # noqa: F401


def make_request(requester, *, status=Status.PENDING, amount="100.00", reviewer=None, **fields):
    reviewed = status in REVIEW_OUTCOMES
    values = {
        "title": "New laptops",
        "justification": "The current ones are five years old.",
        "review_note": "Not this quarter." if status == Status.REJECTED else "",
        "reviewed_at": timezone.now() if reviewed else None,
    }
    values.update(fields)
    return BudgetRequest.objects.create(
        requester=requester, status=status, amount=Decimal(amount), reviewer=reviewer, **values
    )
