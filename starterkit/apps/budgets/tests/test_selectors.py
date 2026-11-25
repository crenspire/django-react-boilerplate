from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.tests.factories import make_request, make_user


class BudgetRequestSelectorTests(TestCase):
    def setUp(self):
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.manager = make_user("manager")

    def test_get(self):
        request = make_request(self.alice)
        self.assertEqual(selectors.budget_request_get(request.pk), request)
        self.assertIsNone(selectors.budget_request_get(request.pk + 1))
        self.assertEqual(selectors.budget_request_get_for_update(request.pk), request)

    def test_requests_for_requester_are_scoped_and_newest_first(self):
        first = make_request(self.alice)
        second = make_request(self.alice)
        make_request(self.bob)
        self.assertEqual(list(selectors.requests_for_requester(self.alice)), [second, first])

    def test_pending_queue_is_oldest_first(self):
        newer = make_request(self.alice)
        older = make_request(self.bob)
        BudgetRequest.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))
        make_request(self.alice, status=Status.APPROVED)
        make_request(self.alice, status=Status.WITHDRAWN)
        self.assertEqual(list(selectors.pending_requests()), [older, newer])

    def test_decided_requests_exclude_pending_and_withdrawn(self):
        now = timezone.now()
        earlier = make_request(self.alice, status=Status.REJECTED, reviewed_at=now - timedelta(hours=1))
        later = make_request(self.bob, status=Status.APPROVED, reviewed_at=now)
        make_request(self.alice)
        make_request(self.alice, status=Status.WITHDRAWN)
        self.assertEqual(list(selectors.decided_requests()), [later, earlier])

    def test_all_requests_with_optional_status_filter(self):
        pending = make_request(self.alice)
        approved = make_request(self.bob, status=Status.APPROVED)
        self.assertEqual(set(selectors.all_requests()), {pending, approved})
        self.assertEqual(list(selectors.all_requests(status=Status.APPROVED)), [approved])

    def test_lists_load_people_without_extra_queries(self):
        for _ in range(3):
            make_request(self.alice, status=Status.APPROVED, reviewer=self.manager)
        with self.assertNumQueries(1):
            names = [(r.requester.username, r.reviewer.username) for r in selectors.all_requests()]
        self.assertEqual(names, [("alice", "manager")] * 3)

    def test_totals_per_status_in_one_query(self):
        make_request(self.alice, amount="100.50")
        make_request(self.bob, amount="200.00")
        make_request(self.alice, amount="1000.00", status=Status.APPROVED)
        make_request(self.alice, amount="7.00", status=Status.REJECTED)

        with self.assertNumQueries(1):
            totals = selectors.totals()

        self.assertEqual(totals["pending_count"], 2)
        self.assertEqual(totals["pending_amount"], Decimal("300.50"))
        self.assertEqual(totals["approved_count"], 1)
        self.assertEqual(totals["approved_amount"], Decimal("1000.00"))
        self.assertEqual(totals["rejected_count"], 1)
        self.assertEqual(totals["withdrawn_count"], 0)

    def test_totals_are_zero_without_requests(self):
        totals = selectors.totals()
        self.assertEqual(totals["pending_amount"], Decimal("0"))
        self.assertEqual(totals["approved_count"], 0)
