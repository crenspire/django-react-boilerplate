import json

from django.test import TestCase

from apps.users.domain.roles import Role
from apps.users.selectors.roles import role_for_user
from apps.users.tests.factories import STRONG_PASSWORD, make_superuser, make_user

INERTIA_HEADERS = {"HTTP_X_INERTIA": "true", "HTTP_X_INERTIA_VERSION": "1.0"}


class WorkspaceViewTests(TestCase):
    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get("/workspace/")
        self.assertRedirects(response, "/admin/login/?next=/workspace/", fetch_redirect_response=False)

    def test_every_role_can_sign_in_and_open_the_workspace(self):
        for role in Role:
            with self.subTest(role=role):
                username = role.value.lower()
                make_user(username, role=role)
                response = self.client.post(
                    "/admin/login/", {"username": username, "password": STRONG_PASSWORD}
                )
                self.assertRedirects(response, "/workspace/", fetch_redirect_response=False)
                page = self.client.get("/workspace/", **INERTIA_HEADERS).json()
                self.assertEqual(page["component"], "Workspace/Home")
                self.assertEqual(page["props"]["role"], role.label)
                self.assertEqual([item["route"] for item in page["props"]["workspace_nav"]], ["workspace"])
                self.assertEqual(page["props"]["admin_nav"], [])


class RoleViewTests(TestCase):
    def setUp(self):
        self.target = make_user("target")
        self.url = f"/admin/users/{self.target.pk}/role/"

    def post(self, role):
        return self.client.post(
            self.url, json.dumps({"role": role}), content_type="application/json", **INERTIA_HEADERS
        )

    def test_superuser_changes_a_role(self):
        self.client.force_login(make_superuser())
        self.assertRedirects(self.post("MANAGER"), "/admin/users/", fetch_redirect_response=False)
        self.assertEqual(role_for_user(self.target), Role.MANAGER)

        users = self.client.get("/admin/users/", **INERTIA_HEADERS).json()["props"]["users"]
        by_name = {user["username"]: user for user in users}
        self.assertEqual((by_name["target"]["role"], by_name["target"]["can_assign_role"]), ("Manager", True))
        self.assertEqual((by_name["root"]["role"], by_name["root"]["can_assign_role"]), ("Admin", False))

    def test_invalid_role_re_renders_the_form(self):
        self.client.force_login(make_superuser())
        page = self.post("OWNER").json()
        self.assertEqual(page["component"], "Admin/Users/Role")
        self.assertEqual(page["props"]["form"], {"role": "CLIENT"})
        self.assertIn("role", page["props"]["errors"])

    def test_other_roles_cannot_view_or_change_roles(self):
        for role in Role:
            self.client.force_login(make_user(role.value, role=role, is_staff=True))
            with self.subTest(role=role):
                self.assertEqual(self.client.get(self.url).status_code, 403)
                self.assertEqual(self.post("ADMIN").status_code, 403)
        self.assertEqual(role_for_user(self.target), Role.CLIENT)


class ErrorPageTests(TestCase):
    def test_403_renders_the_error_page(self):
        self.client.force_login(make_user("client", role=Role.CLIENT))
        response = self.client.get("/admin/users/", **INERTIA_HEADERS)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["X-Inertia"], "true")
        self.assertEqual(response.json()["component"], "Error")

        response = self.client.get("/admin/users/")
        self.assertContains(response, "Access denied", status_code=403, html=False)

    def test_404_renders_the_error_page_for_anonymous_visitors(self):
        response = self.client.get("/nope/", **INERTIA_HEADERS)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["props"]["title"], "Page not found")
