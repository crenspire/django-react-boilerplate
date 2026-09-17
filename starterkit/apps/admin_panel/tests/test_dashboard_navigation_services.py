from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.admin_panel.services.dashboard import RECENT_USERS_LIMIT, get_dashboard_page
from apps.admin_panel.services.navigation import get_admin_navigation
from apps.admin_panel.tests.factories import make_staff, make_superuser, make_user


class DashboardServiceTests(TestCase):
    def test_requires_admin_access(self):
        with self.assertRaises(PermissionDenied):
            get_dashboard_page(actor=make_user("regular"))

    def test_superuser_sees_all_stats(self):
        Group.objects.create(name="Editors")
        make_user("inactive", is_active=False)
        props = get_dashboard_page(actor=make_superuser())
        self.assertEqual(props["user_stats"], {"total": 2, "active": 1, "staff": 1, "superusers": 1})
        self.assertEqual(props["group_stats"], {"total": 1, "permission_assignments": 0})
        self.assertEqual(
            props["can"],
            {"view_users": True, "view_groups": True, "add_users": True, "add_groups": True},
        )

    def test_stats_are_hidden_without_view_permission(self):
        props = get_dashboard_page(actor=make_staff(perms=("view_user",)))
        self.assertIsNotNone(props["user_stats"])
        self.assertIsNone(props["group_stats"])
        self.assertFalse(props["can"]["add_users"])

    def test_recent_users_are_newest_first_with_edit_capability(self):
        root = make_superuser()
        for i in range(RECENT_USERS_LIMIT + 1):
            make_user(f"user{i}")
        staff = make_staff("manager", perms=("change_user",))

        rows = get_dashboard_page(actor=staff)["recent_users"]

        self.assertEqual(len(rows), RECENT_USERS_LIMIT)
        self.assertEqual(rows[0]["username"], "manager")
        self.assertNotIn(root.username, [row["username"] for row in rows])
        by_name = {row["username"]: row for row in rows}
        self.assertFalse(by_name["manager"]["can_edit"])
        self.assertTrue(by_name["user5"]["can_edit"])

    def test_recent_users_hidden_without_view_permission(self):
        make_user("someone")
        self.assertEqual(get_dashboard_page(actor=make_staff())["recent_users"], [])


class NavigationServiceTests(TestCase):
    def routes(self, actor):
        return [item["route"] for item in get_admin_navigation(actor=actor)]

    def test_anonymous_and_non_staff_get_no_navigation(self):
        self.assertEqual(self.routes(AnonymousUser()), [])
        self.assertEqual(self.routes(make_user("regular")), [])

    def test_navigation_is_filtered_by_permissions(self):
        self.assertEqual(self.routes(make_staff()), ["admin_dashboard"])
        self.assertEqual(
            self.routes(make_staff("viewer", perms=("view_group",))),
            ["admin_dashboard", "admin_groups"],
        )
        self.assertEqual(
            self.routes(make_superuser()), ["admin_dashboard", "admin_users", "admin_groups"]
        )

    def test_items_are_grouped_into_sections(self):
        sections = [item["section"] for item in get_admin_navigation(actor=make_superuser())]
        self.assertEqual(sections, ["Overview", "Management", "Management"])
