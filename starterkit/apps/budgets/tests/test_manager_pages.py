from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.budgets.domain.models import Status
from apps.budgets.services import manager_pages
from apps.budgets.services.navigation import get_budget_navigation
from apps.budgets.tests.factories import make_request, make_superuser, make_user
from apps.users.selectors.roles import Role
from shared.dto import ListQueryDTO


def query(page=1):
    return ListQueryDTO(search="", order_by="", page=page, page_size=25)


class ReviewQueuePageTests(TestCase):
    def setUp(self):
        self.manager = make_user("manager", role=Role.MANAGER)
        alice = make_user("alice", role=Role.CLIENT)
        bob = make_user("bob", role=Role.CLIENT)
        self.pending = make_request(alice, amount="100.00")
        make_request(bob, amount="50.25")
        self.approved = make_request(alice, status=Status.APPROVED, reviewer=self.manager)
        make_request(bob, status=Status.REJECTED, reviewer=self.manager)
        make_request(bob, status=Status.WITHDRAWN)

    def test_pending_tab_shows_every_clients_pending_request(self):
        props = manager_pages.get_review_queue_page(actor=self.manager, query=query(), tab="pending")
        self.assertEqual(props["tab"], "pending")
        self.assertEqual([r["requester"] for r in props["requests"]], ["alice", "bob"])
        self.assertTrue(all(r["can"]["review"] for r in props["requests"]))
        self.assertEqual(props["counts"], {"pending": 2, "history": 2})
        self.assertEqual(props["pending_amount"], "150.25")

    def test_history_tab_shows_decisions_that_cannot_be_reviewed_again(self):
        props = manager_pages.get_review_queue_page(actor=self.manager, query=query(), tab="history")
        self.assertEqual({r["status"] for r in props["requests"]}, {"APPROVED", "REJECTED"})
        self.assertFalse(any(r["can"]["review"] for r in props["requests"]))

    def test_unknown_tab_falls_back_to_pending(self):
        props = manager_pages.get_review_queue_page(actor=self.manager, query=query(), tab="<script>")
        self.assertEqual(props["tab"], "pending")

    def test_only_managers_see_the_queue(self):
        for actor in (make_user("c", role=Role.CLIENT), make_user("a", role=Role.ADMIN), make_superuser()):
            with self.subTest(actor=actor.username), self.assertRaises(PermissionDenied):
                manager_pages.get_review_queue_page(actor=actor, query=query(), tab="pending")


class ReviewPageTests(TestCase):
    def setUp(self):
        self.manager = make_user("manager", role=Role.MANAGER)
        self.request = make_request(make_user("alice", role=Role.CLIENT))

    def test_pending_request_can_be_reviewed(self):
        props = manager_pages.get_review_page(actor=self.manager, request_id=self.request.pk)
        self.assertEqual(props["request"]["id"], self.request.pk)
        self.assertTrue(props["request"]["can"]["review"])
        self.assertEqual(props["form"], {"decision": "", "note": ""})

    def test_permission_is_checked_before_existence(self):
        with self.assertRaises(PermissionDenied):
            manager_pages.get_review_page(actor=make_user("a", role=Role.ADMIN), request_id=999_999)
        with self.assertRaises(Http404):
            manager_pages.get_review_page(actor=self.manager, request_id=999_999)

    def test_navigation_shows_the_queue_to_managers_only(self):
        routes = [item["route"] for item in get_budget_navigation(actor=self.manager)]
        self.assertEqual(routes, ["budget_review_queue"])
        client_routes = [item["route"] for item in get_budget_navigation(actor=make_user("c", role=Role.CLIENT))]
        self.assertNotIn("budget_review_queue", client_routes)
