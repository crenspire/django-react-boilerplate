from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.budgets.domain.models import Status
from apps.budgets.services import client_pages
from apps.budgets.services.navigation import get_budget_navigation
from apps.budgets.tests.factories import make_request, make_superuser, make_user
from apps.users.selectors.roles import Role
from shared.dto import ListQueryDTO


def query(page=1, page_size=25):
    return ListQueryDTO(search="", order_by="", page=page, page_size=page_size)


class MyRequestsPageTests(TestCase):
    def setUp(self):
        self.client_user = make_user("client", role=Role.CLIENT)
        self.manager = make_user("manager", role=Role.MANAGER)

    def test_lists_only_the_clients_requests_with_flags(self):
        mine = make_request(self.client_user, amount="12.50")
        make_request(make_user("other", role=Role.CLIENT))
        decided = make_request(
            self.client_user, status=Status.REJECTED, reviewer=self.manager, review_note="Too much"
        )

        props = client_pages.get_my_requests_page(actor=self.client_user, query=query())

        rows = {row["id"]: row for row in props["requests"]}
        self.assertEqual(set(rows), {mine.pk, decided.pk})
        self.assertEqual(rows[mine.pk]["amount"], "12.50")
        self.assertEqual(rows[mine.pk]["can"], {"edit": True, "withdraw": True, "review": False, "delete": False})
        self.assertEqual(rows[decided.pk]["can"]["edit"], False)
        self.assertEqual((rows[decided.pk]["reviewer"], rows[decided.pk]["review_note"]), ("manager", "Too much"))
        self.assertEqual(props["pagination"]["total"], 2)
        self.assertEqual(props["can"], {"create": True})

    def test_pagination(self):
        for _ in range(3):
            make_request(self.client_user)
        props = client_pages.get_my_requests_page(actor=self.client_user, query=query(page=2, page_size=2))
        self.assertEqual(len(props["requests"]), 1)
        self.assertEqual(props["pagination"]["total_pages"], 2)

    def test_other_roles_are_denied(self):
        for actor in (self.manager, make_user("admin", role=Role.ADMIN), make_superuser()):
            with self.subTest(actor=actor.username):
                with self.assertRaises(PermissionDenied):
                    client_pages.get_my_requests_page(actor=actor, query=query())
                with self.assertRaises(PermissionDenied):
                    client_pages.get_create_page(actor=actor)


class EditPageTests(TestCase):
    def setUp(self):
        self.client_user = make_user("client", role=Role.CLIENT)

    def test_pending_request_is_editable(self):
        request = make_request(self.client_user, title="Desk", amount="300.00")
        props = client_pages.get_edit_page(actor=self.client_user, request_id=request.pk)
        self.assertEqual(props["form"], {"title": "Desk", "amount": "300.00", "justification": request.justification})
        self.assertTrue(props["editable"])
        self.assertEqual(props["locked_message"], "")

    def test_decided_request_is_shown_read_only(self):
        request = make_request(self.client_user, status=Status.APPROVED)
        props = client_pages.get_edit_page(actor=self.client_user, request_id=request.pk)
        self.assertFalse(props["editable"])
        self.assertEqual(props["locked_message"], client_pages.LOCKED_MESSAGE)

    def test_other_clients_get_404_and_managers_403(self):
        request = make_request(self.client_user)
        with self.assertRaises(Http404):
            client_pages.get_edit_page(actor=make_user("other", role=Role.CLIENT), request_id=request.pk)
        with self.assertRaises(PermissionDenied):
            client_pages.get_edit_page(actor=make_user("m", role=Role.MANAGER), request_id=request.pk)
        with self.assertRaises(Http404):
            client_pages.get_edit_page(actor=self.client_user, request_id=999_999)


class BudgetNavigationTests(TestCase):
    def routes(self, actor):
        return [item["route"] for item in get_budget_navigation(actor=actor)]

    def test_each_role_sees_its_own_pages(self):
        self.assertEqual(
            self.routes(make_user("client", role=Role.CLIENT)), ["budget_my_requests", "budget_request_create"]
        )
        self.assertEqual(self.routes(make_user("manager", role=Role.MANAGER)), ["budget_review_queue"])
        self.assertEqual(self.routes(AnonymousUser()), [])
