from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.users.domain.roles import Role
from apps.users.selectors import roles as role_selectors
from apps.users.tests.factories import make_superuser, make_user


class RoleSelectorTests(TestCase):
    def test_user_get(self):
        user = make_user("user")
        self.assertEqual(role_selectors.user_get(user.pk), user)
        self.assertIsNone(role_selectors.user_get(user.pk + 1))

    def test_stored_role(self):
        self.assertEqual(role_selectors.stored_role(make_user("m", role=Role.MANAGER)), Role.MANAGER)
        self.assertIsNone(role_selectors.stored_role(make_user("new")))

    def test_role_for_user(self):
        self.assertEqual(role_selectors.role_for_user(make_user("m", role=Role.MANAGER)), Role.MANAGER)
        self.assertEqual(role_selectors.role_for_user(make_user("new")), Role.CLIENT)
        self.assertEqual(role_selectors.role_for_user(make_superuser()), Role.ADMIN)
        self.assertIsNone(role_selectors.role_for_user(AnonymousUser()))


class UserProfileConstraintTests(TestCase):
    def test_database_rejects_unknown_roles(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_user("bad", role="OWNER")


class RolesForUsersTests(TestCase):
    def test_resolves_many_users_with_one_query(self):
        manager = make_user("m", role=Role.MANAGER)
        new = make_user("new")
        root = make_superuser()
        inactive = make_user("inactive", role=Role.ADMIN, is_active=False)
        with self.assertNumQueries(1):
            roles = role_selectors.roles_for_users([manager, new, root, inactive])
        self.assertEqual(
            roles,
            {manager.pk: Role.MANAGER, new.pk: Role.CLIENT, root.pk: Role.ADMIN, inactive.pk: None},
        )
