from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.selectors import budget_requests as selectors
from apps.users.selectors.roles import user_get_by_username

DEMO_REQUESTS = (
    ("client1", "Design team laptops", "4800.00", "Three laptops are over five years old and slow down builds.", Status.PENDING, "", 2),
    ("client1", "Conference tickets", "1250.00", "Two engineers presenting at DjangoCon.", Status.APPROVED, "Good visibility for the team.", 9),
    ("client1", "Office plants", "180.50", "Brighten up the shared workspace.", Status.REJECTED, "Not a priority this quarter.", 6),
    ("client1", "Standing desks", "2100.00", "Requested by the support team.", Status.WITHDRAWN, "", 4),
    ("client2", "Cloud hosting upgrade", "950.00", "Staging runs out of memory during load tests.", Status.PENDING, "", 1),
    ("client2", "Customer research incentives", "600.00", "Gift cards for twelve interview participants.", Status.PENDING, "", 3),
    ("client2", "Team offsite", "3500.00", "Quarterly planning offsite for eight people.", Status.APPROVED, "", 12),
)

REQUIRED_USERS = ("client1", "client2", "manager1")


@transaction.atomic
def seed_demo_requests() -> int:
    users = {username: user_get_by_username(username) for username in REQUIRED_USERS}
    missing = [username for username, user in users.items() if user is None]
    if missing:
        raise ValueError(f"Create the demo users first: {', '.join(missing)}.")

    created = 0
    now = timezone.now()
    for username, title, amount, justification, status, note, days_ago in DEMO_REQUESTS:
        requester = users[username]
        if selectors.request_exists_for(requester, title):
            continue
        decided = status in (Status.APPROVED, Status.REJECTED)
        request = BudgetRequest.objects.create(
            requester=requester,
            title=title,
            amount=Decimal(amount),
            justification=justification,
            status=status,
            reviewer=users["manager1"] if decided else None,
            review_note=note,
            reviewed_at=now - timedelta(days=days_ago - 1) if decided else None,
        )
        BudgetRequest.objects.filter(pk=request.pk).update(created_at=now - timedelta(days=days_ago))
        created += 1
    return created
