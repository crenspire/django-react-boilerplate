from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q


class Status(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


REVIEW_OUTCOMES = (Status.APPROVED, Status.REJECTED)

MAX_AMOUNT = Decimal("9999999999.99")


class BudgetRequest(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    justification = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budget_requests"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_budget_requests",
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["status", "created_at"])]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="budget_amount_positive"),
            models.CheckConstraint(condition=Q(status__in=Status.values), name="budget_status_valid"),
            models.CheckConstraint(
                condition=Q(status__in=REVIEW_OUTCOMES, reviewed_at__isnull=False)
                | (~Q(status__in=REVIEW_OUTCOMES) & Q(reviewed_at__isnull=True)),
                name="budget_reviewed_at_matches_status",
            ),
            models.CheckConstraint(
                condition=~Q(status=Status.REJECTED) | ~Q(review_note=""),
                name="budget_rejection_has_note",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_pending(self) -> bool:
        return self.status == Status.PENDING
