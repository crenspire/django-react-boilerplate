import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import Client, TestCase

from apps.admin_panel.tests.factories import STRONG_PASSWORD, USER_PERMS, make_staff, make_superuser, make_user

User = get_user_model()

INERTIA_HEADERS = {"HTTP_X_INERTIA": "true", "HTTP_X_INERTIA_VERSION": "1.0"}


class InertiaClientMixin:
    def page(self, response):
        self.assertEqual(response.status_code, 200, response.content[:500])
        return response.json()

    def post_json(self, client, url, data):
        return client.post(url, json.dumps(data), content_type="application/json", **INERTIA_HEADERS)


class AccessTests(InertiaClientMixin, TestCase):
    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get("/admin/users/")
        self.assertRedirects(response, "/admin/login/?next=/admin/users/", fetch_redirect_response=False)

    def test_staff_without_permission_gets_403(self):
        self.client.force_login(make_staff())
        self.assertEqual(self.client.get("/admin/users/").status_code, 403)
        self.assertEqual(self.client.get("/admin/groups/").status_code, 403)

    def test_delete_requires_post(self):
        self.client.force_login(make_superuser())
        target = make_user("target")
        self.assertEqual(self.client.get(f"/admin/users/{target.pk}/delete/").status_code, 405)

    def test_missing_user_returns_404(self):
        self.client.force_login(make_superuser())
        self.assertEqual(self.client.get("/admin/users/999999/edit/").status_code, 404)


class UserViewTests(InertiaClientMixin, TestCase):
    def setUp(self):
        self.root = make_superuser()
        self.client.force_login(self.root)

    def test_list_tolerates_garbage_query_params(self):
        response = self.client.get(
            "/admin/users/?page=abc&page_size=-4&order_by=password", **INERTIA_HEADERS
        )
        props = self.page(response)["props"]
        self.assertEqual(props["pagination"]["page"], 1)
        self.assertEqual(props["pagination"]["page_size"], 1)
        self.assertEqual(props["filters"]["order_by"], "username")

    def test_shared_props_are_present(self):
        props = self.page(self.client.get("/admin/", **INERTIA_HEADERS))["props"]
        self.assertEqual(props["auth"]["user"]["username"], "root")
        self.assertNotIn("is_superuser", props["auth"]["user"])
        self.assertEqual(props["routes"]["admin_user_edit"], "/admin/users/{user_id}/edit/")
        self.assertEqual(
            [item["route"] for item in props["admin_nav"]],
            ["admin_dashboard", "admin_users", "admin_groups"],
        )

    def test_create_redirects_with_flash_message(self):
        response = self.post_json(
            self.client,
            "/admin/users/create/",
            {"username": "newbie", "password": STRONG_PASSWORD, "is_active": True, "group_ids": []},
        )
        user = User.objects.get(username="newbie")
        self.assertRedirects(response, f"/admin/users/{user.pk}/edit/", fetch_redirect_response=False)

        props = self.page(self.client.get(response["Location"], **INERTIA_HEADERS))["props"]
        self.assertEqual(props["flash"], [{"level": "success", "message": 'User "newbie" was created.'}])

    def test_create_validation_error_re_renders_form(self):
        response = self.post_json(self.client, "/admin/users/create/", {"username": "", "password": "1"})
        page = self.page(response)
        self.assertEqual(page["component"], "Admin/Users/Create")
        self.assertIn("username", page["props"]["errors"])
        self.assertIn("password", page["props"]["errors"])
        self.assertTrue(page["props"]["groups_choices"] is not None)

    def test_form_encoded_unchecked_active_means_inactive(self):
        self.client.post(
            "/admin/users/create/", {"username": "formuser", "password": STRONG_PASSWORD}
        )
        self.assertFalse(User.objects.get(username="formuser").is_active)

    def test_failed_delete_keeps_list_and_shows_error(self):
        response = self.client.post(f"/admin/users/{self.root.pk}/delete/", **INERTIA_HEADERS)
        self.assertRedirects(response, "/admin/users/", fetch_redirect_response=False)

        props = self.page(self.client.get("/admin/users/", **INERTIA_HEADERS))["props"]
        self.assertEqual(len(props["users"]), 1)
        self.assertEqual(props["flash"][0]["level"], "error")

    def test_staff_cannot_escalate_through_http(self):
        staff = make_staff("climber", perms=USER_PERMS)
        client = Client()
        client.force_login(staff)

        response = self.post_json(
            client,
            f"/admin/users/{staff.pk}/edit/",
            {"username": "climber", "is_staff": True, "is_superuser": True, "is_active": True},
        )

        self.assertEqual(response.status_code, 403)
        staff.refresh_from_db()
        self.assertFalse(staff.is_superuser)


class GroupViewTests(InertiaClientMixin, TestCase):
    def setUp(self):
        self.client.force_login(make_superuser())

    def test_delete_redirects_with_flash(self):
        group = Group.objects.create(name="Old")
        response = self.client.post(f"/admin/groups/{group.pk}/delete/")
        self.assertRedirects(response, "/admin/groups/", fetch_redirect_response=False)
        self.assertFalse(Group.objects.filter(pk=group.pk).exists())

    def test_create_and_edit_round_trip(self):
        response = self.post_json(self.client, "/admin/groups/create/", {"name": "Editors", "permission_ids": []})
        group = Group.objects.get(name="Editors")
        self.assertRedirects(response, f"/admin/groups/{group.pk}/edit/", fetch_redirect_response=False)

        page = self.page(self.client.get(response["Location"], **INERTIA_HEADERS))
        self.assertEqual(page["props"]["group"], {"id": group.pk, "name": "Editors"})


class AuthViewTests(InertiaClientMixin, TestCase):
    def setUp(self):
        cache.clear()
        self.staff = make_staff("staffuser")

    def test_login_and_logout_with_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.get("/admin/login/")
        token = client.cookies["csrftoken"].value

        response = client.post(
            "/admin/login/",
            json.dumps({"username": "staffuser", "password": STRONG_PASSWORD, "next": "/admin/users/"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
            **INERTIA_HEADERS,
        )
        self.assertRedirects(response, "/admin/users/", fetch_redirect_response=False)

        # Django rotates the CSRF token on login.
        token = client.cookies["csrftoken"].value
        response = client.post("/logout/", HTTP_X_CSRFTOKEN=token, **INERTIA_HEADERS)
        self.assertRedirects(response, "/admin/login/", fetch_redirect_response=False)

    def test_foreign_xsrf_token_cookie_does_not_break_csrf(self):
        # Laravel/Angular apps on the same host set an XSRF-TOKEN cookie in a
        # format Django rejects; it must not be used for Django's CSRF check.
        client = Client(enforce_csrf_checks=True)
        client.get("/admin/login/")
        client.cookies["XSRF-TOKEN"] = "x" * 92
        token = client.cookies["csrftoken"].value

        response = client.post(
            "/admin/login/",
            json.dumps({"username": "staffuser", "password": STRONG_PASSWORD}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
            **INERTIA_HEADERS,
        )

        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)

    def test_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/admin/login/", {"username": "staffuser", "password": STRONG_PASSWORD})
        self.assertEqual(response.status_code, 403)

    def test_failed_login_re_renders_without_password(self):
        response = self.post_json(self.client, "/admin/login/", {"username": "staffuser", "password": "nope"})
        props = self.page(response)["props"]
        self.assertEqual(props["form"], {"username": "staffuser", "password": "", "next": ""})
        self.assertIn("non_field_errors", props["errors"])

    def test_logout_shows_signed_out_message_on_login_page(self):
        self.client.force_login(self.staff)
        response = self.client.post("/logout/", **INERTIA_HEADERS)
        props = self.page(self.client.get(response["Location"], **INERTIA_HEADERS))["props"]
        self.assertEqual(props["flash"], [{"level": "info", "message": "You have been signed out."}])

    def test_logout_requires_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/logout/").status_code, 405)
