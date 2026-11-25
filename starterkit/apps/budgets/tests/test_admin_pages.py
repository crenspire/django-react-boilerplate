from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.services import admin_pages
from apps.budgets.services.navigation import get_budget_navigation
from apps.budgets.tests.factories import make_request, make_superuser, make_user
from apps.users.selectors.roles import Role
from shared.dto import ListQueryDTO


def query(page=1):
    return ListQueryDTO(search="", order_by="", page=page, page_size=25)


class OverviewPageTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin", role=Role.ADMIN)
        manager = make_user("manager", role=Role.MANAGER)
        alice = make_user("alice", role=Role.CLIENT)
        make_request(alice, amount="100.00")
        make_request(alice, amount="50.25")
        make_request(alice, status=Status.APPROVED, amount="1000.00", reviewer=manager)
        make_request(alice, status=Status.REJECTED, amount="7.00", reviewer=manager)
        make_request(alice, status=Status.WITHDRAWN, amount="3.00")

    def test_summary_totals_by_status(self):
        summary = admin_pages.get_overview_page(actor=self.admin, query=query(), status="")["summary"]
        self.assertEqual(summary["pending"], {"label": "Pending", "count": 2, "amount": "150.25"})
        self.assertEqual(summary["approved"], {"label": "Approved", "count": 1, "amount": "1000.00"})
        self.assertEqual((summary["rejected"]["count"], summary["withdrawn"]["count"]), (1, 1))
        self.assertEqual((summary["total"]["count"], summary["total"]["amount"]), (5, "1160.25"))

    def test_lists_every_request_with_delete_flag(self):
        props = admin_pages.get_overview_page(actor=self.admin, query=query(), status="")
        self.assertEqual(props["status"], "")
        self.assertEqual(len(props["requests"]), 5)
        self.assertTrue(all(r["can"]["delete"] for r in props["requests"]))
        self.assertFalse(any(r["can"]["review"] or r["can"]["edit"] for r in props["requests"]))

    def test_status_filter(self):
        props = admin_pages.get_overview_page(actor=self.admin, query=query(), status="APPROVED")
        self.assertEqual([r["status"] for r in props["requests"]], ["APPROVED"])
        self.assertEqual(props["summary"]["pending"]["count"], 2)

    def test_unknown_status_shows_everything(self):
        props = admin_pages.get_overview_page(actor=self.admin, query=query(), status="DELETED")
        self.assertEqual(props["status"], "")
        self.assertEqual(len(props["requests"]), 5)

    def test_empty_database_has_zero_totals(self):
        BudgetRequest.objects.all().delete()
        summary = admin_pages.get_overview_page(actor=self.admin, query=query(), status="")["summary"]
        self.assertEqual((summary["total"]["count"], summary["total"]["amount"]), (0, "0.00"))
        self.assertEqual(summary["approved"], {"label": "Approved", "count": 0, "amount": "0.00"})

    def test_superuser_is_an_admin(self):
        props = admin_pages.get_overview_page(actor=make_superuser(), query=query(), status="")
        self.assertEqual(len(props["requests"]), 5)

    def test_clients_and_managers_are_denied(self):
        for role in (Role.CLIENT, Role.MANAGER):
            with self.subTest(role=role), self.assertRaises(PermissionDenied):
                admin_pages.get_overview_page(actor=make_user(f"u-{role}", role=role), query=query(), status="")

    def test_navigation_shows_overview_to_admins_only(self):
        self.assertEqual([i["route"] for i in get_budget_navigation(actor=self.admin)], ["budget_overview"])
        manager_routes = [i["route"] for i in get_budget_navigation(actor=make_user("m2", role=Role.MANAGER))]
        self.assertNotIn("budget_overview", manager_routes)
