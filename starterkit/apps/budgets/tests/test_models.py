from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.tests.factories import make_request, make_user


class BudgetRequestConstraintTests(TestCase):
    def setUp(self):
        self.client_user = make_user("client")

    def assert_rejected_by_database(self, **fields):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_request(self.client_user, **fields)

    def test_defaults(self):
        request = make_request(self.client_user)
        self.assertEqual(request.status, Status.PENDING)
        self.assertTrue(request.is_pending)
        self.assertIsNone(request.reviewer)

    def test_amount_must_be_positive(self):
        self.assert_rejected_by_database(amount="0.00")
        self.assert_rejected_by_database(amount="-5.00")

    def test_status_must_be_known(self):
        self.assert_rejected_by_database(status="CANCELLED")

    def test_rejection_requires_a_note(self):
        self.assert_rejected_by_database(status=Status.REJECTED, review_note="")
        make_request(self.client_user, status=Status.APPROVED, review_note="")

    def test_reviewed_at_matches_status(self):
        self.assert_rejected_by_database(status=Status.APPROVED, reviewed_at=None)
        self.assert_rejected_by_database(status=Status.PENDING, reviewed_at=timezone.now())
        self.assert_rejected_by_database(status=Status.WITHDRAWN, reviewed_at=timezone.now())

    def test_deleting_the_reviewer_keeps_the_decision(self):
        manager = make_user("manager")
        request = make_request(self.client_user, status=Status.APPROVED, reviewer=manager)
        manager.delete()
        request.refresh_from_db()
        self.assertIsNone(request.reviewer)
        self.assertEqual(request.status, Status.APPROVED)

    def test_deleting_the_requester_deletes_their_requests(self):
        make_request(self.client_user)
        self.client_user.delete()
        self.assertFalse(BudgetRequest.objects.exists())
