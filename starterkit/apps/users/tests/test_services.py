from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.users.domain.roles import Role
from apps.users.dto.roles import AssignRoleInputDTO
from apps.users.selectors.roles import role_for_user, stored_role
from apps.users.services.roles import (
    FIXED_ROLE_ERROR,
    INVALID_ROLE_ERROR,
    assign_role,
    get_role_page,
)
from apps.users.services.workspace import get_workspace_navigation, get_workspace_page
from apps.users.tests.factories import make_superuser, make_user


class AssignRoleTests(TestCase):
    def setUp(self):
        self.superuser = make_superuser()

    def assign(self, user_id, role, actor=None):
        return assign_role(
            actor=actor or self.superuser, data=AssignRoleInputDTO(user_id=user_id, role=role)
        )

    def test_creates_a_profile_for_a_user_without_one(self):
        user = make_user("new")
        self.assertTrue(self.assign(user.pk, "MANAGER").success)
        self.assertEqual(role_for_user(user), Role.MANAGER)

    def test_replaces_an_existing_role(self):
        user = make_user("user", role=Role.MANAGER)
        result = self.assign(user.pk, "CLIENT")
        self.assertTrue(result.success)
        self.assertEqual(result.message, '"user" now has the Client role.')
        self.assertEqual(role_for_user(user), Role.CLIENT)

    def test_rejects_unknown_roles(self):
        user = make_user("user", role=Role.MANAGER)
        for role in ("OWNER", "manager", ""):
            with self.subTest(role=role):
                result = self.assign(user.pk, role)
                self.assertFalse(result.success)
                self.assertEqual(result.errors, {"role": [INVALID_ROLE_ERROR]})
        self.assertEqual(stored_role(user), Role.MANAGER)

    def test_superuser_role_is_fixed(self):
        other = make_superuser("other")
        result = self.assign(other.pk, "CLIENT")
        self.assertFalse(result.success)
        self.assertEqual(result.errors, {"role": [FIXED_ROLE_ERROR]})
        self.assertIsNone(stored_role(other))

    def test_non_superusers_are_denied(self):
        target = make_user("target", role=Role.CLIENT)
        for role in Role:
            actor = make_user(f"actor-{role.value}", role=role, is_staff=True)
            with self.subTest(role=role), self.assertRaises(PermissionDenied):
                self.assign(target.pk, "ADMIN", actor=actor)
        with self.assertRaises(PermissionDenied):
            self.assign(target.pk, "ADMIN", actor=target)
        self.assertEqual(stored_role(target), Role.CLIENT)

    def test_unknown_user_is_404(self):
        with self.assertRaises(Http404):
            self.assign(999_999, "CLIENT")


class RolePageTests(TestCase):
    def test_props_for_a_regular_user(self):
        user = make_user("user", role=Role.MANAGER)
        props = get_role_page(actor=make_superuser(), user_id=user.pk)
        self.assertEqual(props["user"], {"id": user.pk, "username": "user"})
        self.assertEqual(props["form"], {"role": "MANAGER"})
        self.assertEqual([choice["value"] for choice in props["role_choices"]], Role.values)
        self.assertEqual(props["fixed_role_message"], "")

    def test_superuser_target_is_shown_as_fixed_admin(self):
        root = make_superuser()
        props = get_role_page(actor=root, user_id=root.pk)
        self.assertEqual(props["form"], {"role": "ADMIN"})
        self.assertEqual(props["fixed_role_message"], FIXED_ROLE_ERROR)

    def test_permission_is_checked_before_existence(self):
        with self.assertRaises(PermissionDenied):
            get_role_page(actor=make_user("admin", role=Role.ADMIN), user_id=999_999)


class WorkspaceServiceTests(TestCase):
    def test_page_describes_the_actors_role(self):
        props = get_workspace_page(actor=make_user("m", role=Role.MANAGER, first_name="Mia"))
        self.assertEqual((props["display_name"], props["role"]), ("Mia", "Manager"))

    def test_inactive_and_anonymous_users_are_denied(self):
        for actor in (make_user("inactive", is_active=False), AnonymousUser()):
            with self.assertRaises(PermissionDenied):
                get_workspace_page(actor=actor)
            self.assertEqual(get_workspace_navigation(actor=actor), [])
