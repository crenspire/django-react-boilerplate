from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.users.domain import policies
from apps.users.domain.roles import Role, effective_role
from apps.users.tests.factories import make_superuser, make_user


class EffectiveRoleTests(TestCase):
    def test_anonymous_has_no_role(self):
        self.assertIsNone(effective_role(AnonymousUser(), None))

    def test_inactive_user_has_no_role_even_when_privileged(self):
        self.assertIsNone(effective_role(make_user("inactive", is_active=False), Role.ADMIN))
        self.assertIsNone(effective_role(make_superuser(is_active=False), None))

    def test_missing_profile_falls_back_to_client(self):
        self.assertEqual(effective_role(make_user("new"), None), Role.CLIENT)

    def test_staff_status_alone_grants_no_extra_role(self):
        self.assertEqual(effective_role(make_user("staff", is_staff=True), None), Role.CLIENT)

    def test_stored_role_is_used(self):
        user = make_user("user")
        for role in Role:
            with self.subTest(role=role):
                self.assertEqual(effective_role(user, role.value), role)

    def test_superuser_is_always_admin(self):
        self.assertEqual(effective_role(make_superuser(), Role.CLIENT), Role.ADMIN)


class AssignRolePolicyTests(TestCase):
    def test_only_active_superusers_can_assign_roles(self):
        self.assertTrue(policies.can_assign_roles(make_superuser()))
        self.assertFalse(policies.can_assign_roles(make_superuser("inactive", is_active=False)))
        self.assertFalse(policies.can_assign_roles(make_user("admin", role=Role.ADMIN)))
        self.assertFalse(policies.can_assign_roles(make_user("staff", is_staff=True)))
        self.assertFalse(policies.can_assign_roles(AnonymousUser()))

    def test_only_superusers_have_a_fixed_role(self):
        self.assertTrue(policies.has_fixed_role(make_superuser()))
        self.assertFalse(policies.has_fixed_role(make_user("admin", role=Role.ADMIN)))


class WorkspacePolicyTests(TestCase):
    def test_every_role_but_no_role_may_access_the_workspace(self):
        for role in Role:
            self.assertTrue(policies.can_access_workspace(role))
        self.assertFalse(policies.can_access_workspace(None))
