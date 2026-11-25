from io import StringIO

from django.contrib.auth import authenticate
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services.demo import DEMO_REQUESTS, seed_demo_requests
from apps.budgets.tests.factories import make_request
from apps.users.selectors.roles import Role, role_for_user, user_get_by_username


def run_seed():
    out = StringIO()
    call_command("seed_demo", stdout=out)
    return out.getvalue()


@override_settings(DEBUG=True)
class SeedDemoCommandTests(TestCase):
    def test_creates_an_account_for_every_role(self):
        output = run_seed()
        for username, role in (("client1", Role.CLIENT), ("manager1", Role.MANAGER), ("admin1", Role.ADMIN)):
            with self.subTest(username=username):
                user = authenticate(username=username, password="budget-demo-2026")
                self.assertIsNotNone(user)
                self.assertEqual(role_for_user(user), role)
                self.assertIn(username, output)

    def test_creates_requests_in_every_status(self):
        run_seed()
        self.assertEqual(BudgetRequest.objects.count(), len(DEMO_REQUESTS))
        self.assertEqual(set(BudgetRequest.objects.values_list("status", flat=True)), set(Status.values))
        manager = user_get_by_username("manager1")
        for request in BudgetRequest.objects.filter(status__in=(Status.APPROVED, Status.REJECTED)):
            self.assertEqual(request.reviewer, manager)
        self.assertEqual(selectors.pending_requests().first().title, "Customer research incentives")

    def test_running_twice_does_not_duplicate(self):
        run_seed()
        output = run_seed()
        self.assertEqual(BudgetRequest.objects.count(), len(DEMO_REQUESTS))
        self.assertIn("Created 0 demo budget requests.", output)

    def test_keeps_existing_requests(self):
        run_seed()
        make_request(user_get_by_username("client1"), title="Extra")
        run_seed()
        self.assertEqual(BudgetRequest.objects.count(), len(DEMO_REQUESTS) + 1)


class SeedDemoSafetyTests(TestCase):
    @override_settings(DEBUG=False)
    def test_refuses_to_run_without_debug(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertIsNone(user_get_by_username("client1"))

    def test_requests_need_the_demo_users(self):
        with self.assertRaises(ValueError):
            seed_demo_requests()
