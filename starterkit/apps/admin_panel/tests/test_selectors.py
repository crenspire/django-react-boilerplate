from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from apps.admin_panel.selectors import auth as auth_selectors
from apps.admin_panel.selectors import groups as group_selectors
from apps.admin_panel.selectors import users as user_selectors
from apps.admin_panel.tests.factories import make_user


class UserSelectorsTests(TestCase):
    def setUp(self):
        self.alice = make_user("alice", email="alice@example.com")
        make_user("bob", email="bob@example.com")
        make_user("charlie", email="charlie@test.com")

    def test_user_list_searches_username_and_email(self):
        self.assertEqual([u.username for u in user_selectors.user_list(search="alice")], ["alice"])
        self.assertEqual(
            [u.username for u in user_selectors.user_list(search="test.com")], ["charlie"]
        )

    def test_user_list_orders(self):
        usernames = [u.username for u in user_selectors.user_list(order_by="-username")]
        self.assertEqual(usernames, ["charlie", "bob", "alice"])

    def test_user_get_returns_none_for_missing_user(self):
        self.assertEqual(user_selectors.user_get(self.alice.pk), self.alice)
        self.assertIsNone(user_selectors.user_get(999_999))

    def test_user_group_ids(self):
        group = Group.objects.create(name="Editors")
        self.alice.groups.add(group)
        self.assertEqual(user_selectors.user_group_ids(self.alice), [group.pk])


class GroupSelectorsTests(TestCase):
    def test_group_list_counts_are_not_multiplied_by_joins(self):
        group = Group.objects.create(name="Editors")
        for i in range(3):
            make_user(f"user{i}").groups.add(group)
        group.permissions.set(Permission.objects.all()[:4])

        row = group_selectors.group_list().get(pk=group.pk)

        self.assertEqual(row.user_count, 3)
        self.assertEqual(row.permission_count, 4)

    def test_group_list_search(self):
        Group.objects.create(name="Admins")
        Group.objects.create(name="Editors")
        self.assertEqual([g.name for g in group_selectors.group_list(search="adm")], ["Admins"])

    def test_groups_and_permissions_by_ids(self):
        group = Group.objects.create(name="Admins")
        Group.objects.create(name="Other")
        self.assertEqual(list(group_selectors.groups_by_ids([group.pk])), [group])

        permission = Permission.objects.first()
        self.assertEqual(list(group_selectors.permissions_by_ids([permission.pk])), [permission])

    def test_group_permission_ids(self):
        group = Group.objects.create(name="Admins")
        permission = Permission.objects.first()
        group.permissions.add(permission)
        self.assertEqual(group_selectors.group_permission_ids(group), [permission.pk])


class AuthSelectorsTests(TestCase):
    def test_user_counts(self):
        make_user("alice")
        make_user("bob", is_active=False)
        make_user("carol", is_staff=True)
        make_user("root", is_staff=True, is_superuser=True)
        self.assertEqual(
            auth_selectors.user_counts(),
            {"total": 4, "active": 3, "staff": 2, "superusers": 1},
        )

    def test_group_counts(self):
        group = Group.objects.create(name="Admins")
        Group.objects.create(name="Empty")
        group.permissions.set(Permission.objects.all()[:3])
        self.assertEqual(auth_selectors.count_groups(), 2)
        self.assertEqual(auth_selectors.count_group_permission_assignments(), 3)


class RecentUsersSelectorTests(TestCase):
    def test_newest_first_and_limited(self):
        for name in ("first", "second", "third"):
            make_user(name)
        self.assertEqual(
            [u.username for u in user_selectors.recent_users(limit=2)], ["third", "second"]
        )
