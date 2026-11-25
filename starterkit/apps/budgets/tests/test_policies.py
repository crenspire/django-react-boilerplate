from django.test import TestCase

from apps.budgets.domain import policies
from apps.budgets.domain.models import Status
from apps.budgets.tests.factories import make_request, make_user
from apps.users.selectors.roles import Role

ALL_ROLES = (*Role, None)


class ListPolicyTests(TestCase):
    def assert_only(self, check, allowed_role):
        for role in ALL_ROLES:
            with self.subTest(check=check.__name__, role=role):
                self.assertEqual(check(role), role == allowed_role)

    def test_each_list_belongs_to_one_role(self):
        self.assert_only(policies.can_create, Role.CLIENT)
        self.assert_only(policies.can_view_own_requests, Role.CLIENT)
        self.assert_only(policies.can_view_review_queue, Role.MANAGER)
        self.assert_only(policies.can_view_all_requests, Role.ADMIN)
        self.assert_only(policies.can_delete, Role.ADMIN)


class RequestPolicyTests(TestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.other = make_user("other")
        self.pending = make_request(self.owner)
        self.decided = {
            status: make_request(self.owner, status=status)
            for status in (Status.APPROVED, Status.REJECTED, Status.WITHDRAWN)
        }

    def test_clients_see_only_their_own_requests(self):
        self.assertTrue(policies.can_view(self.owner, Role.CLIENT, self.pending))
        self.assertFalse(policies.can_view(self.other, Role.CLIENT, self.pending))

    def test_managers_and_admins_see_every_request(self):
        for role in (Role.MANAGER, Role.ADMIN):
            self.assertTrue(policies.can_view(self.other, role, self.pending))
        self.assertFalse(policies.can_view(self.owner, None, self.pending))

    def test_only_the_owner_edits_or_withdraws_and_only_while_pending(self):
        for check in (policies.can_edit, policies.can_withdraw):
            with self.subTest(check=check.__name__):
                self.assertTrue(check(self.owner, Role.CLIENT, self.pending))
                self.assertFalse(check(self.other, Role.CLIENT, self.pending))
                for request in self.decided.values():
                    self.assertFalse(check(self.owner, Role.CLIENT, request))
                self.assertFalse(check(self.owner, Role.MANAGER, self.pending))
                self.assertFalse(check(self.owner, Role.ADMIN, self.pending))

    def test_only_managers_review_and_only_pending_requests(self):
        self.assertTrue(policies.can_review(Role.MANAGER, self.pending))
        for request in self.decided.values():
            self.assertFalse(policies.can_review(Role.MANAGER, request))
        for role in (Role.CLIENT, Role.ADMIN, None):
            self.assertFalse(policies.can_review(role, self.pending))
