from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.admin_panel.domain import policies
from apps.admin_panel.tests.factories import GROUP_PERMS, USER_PERMS, make_staff, make_superuser, make_user


class AdminAccessPolicyTests(TestCase):
    def test_anonymous_cannot_access_admin(self):
        self.assertFalse(policies.can_access_admin(AnonymousUser()))

    def test_non_staff_cannot_access_admin(self):
        self.assertFalse(policies.can_access_admin(make_user("regular")))

    def test_inactive_staff_cannot_access_admin(self):
        self.assertFalse(policies.can_access_admin(make_staff(is_active=False)))

    def test_active_staff_can_access_admin(self):
        self.assertTrue(policies.can_access_admin(make_staff()))

    def test_only_superusers_can_grant_privileges(self):
        self.assertFalse(policies.can_grant_privileges(make_staff(perms=USER_PERMS)))
        self.assertTrue(policies.can_grant_privileges(make_superuser()))


class UserPolicyTests(TestCase):
    def test_staff_without_model_permissions_cannot_manage_users(self):
        staff = make_staff()
        self.assertFalse(policies.can_view_users(staff))
        self.assertFalse(policies.can_add_users(staff))
        self.assertFalse(policies.can_change_users(staff))
        self.assertFalse(policies.can_delete_users(staff))

    def test_model_permissions_grant_matching_actions(self):
        staff = make_staff(perms=("view_user",))
        self.assertTrue(policies.can_view_users(staff))
        self.assertFalse(policies.can_change_users(staff))

    def test_change_permission_implies_view(self):
        self.assertTrue(policies.can_view_users(make_staff(perms=("change_user",))))

    def test_non_superuser_cannot_change_privileged_accounts(self):
        staff = make_staff(perms=USER_PERMS)
        self.assertTrue(policies.can_change_user(staff, make_user("regular")))
        self.assertFalse(policies.can_change_user(staff, make_staff("other")))
        self.assertFalse(policies.can_change_user(staff, make_superuser()))

    def test_superuser_can_change_privileged_accounts(self):
        self.assertTrue(policies.can_change_user(make_superuser(), make_staff("other")))

    def test_nobody_can_delete_themselves(self):
        root = make_superuser()
        self.assertFalse(policies.can_delete_user(root, root))

    def test_non_superuser_cannot_delete_privileged_accounts(self):
        staff = make_staff(perms=USER_PERMS)
        self.assertTrue(policies.can_delete_user(staff, make_user("regular")))
        self.assertFalse(policies.can_delete_user(staff, make_superuser()))


class GroupPolicyTests(TestCase):
    def test_group_actions_require_model_permissions(self):
        self.assertFalse(policies.can_view_groups(make_staff()))
        staff = make_staff("groupie", perms=GROUP_PERMS)
        self.assertTrue(policies.can_view_groups(staff))
        self.assertTrue(policies.can_add_groups(staff))
        self.assertTrue(policies.can_change_groups(staff))
        self.assertTrue(policies.can_delete_groups(staff))

    def test_only_superusers_can_assign_permissions(self):
        self.assertFalse(policies.can_assign_permissions(make_staff(perms=GROUP_PERMS)))
        self.assertTrue(policies.can_assign_permissions(make_superuser()))
