import json

from django.test import TestCase

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.tests.factories import make_request, make_user
from apps.users.selectors.roles import Role

INERTIA_HEADERS = {"HTTP_X_INERTIA": "true", "HTTP_X_INERTIA_VERSION": "1.0"}


class ClientViewTests(TestCase):
    def setUp(self):
        self.client_user = make_user("client", role=Role.CLIENT)
        self.client.force_login(self.client_user)

    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type="application/json", **INERTIA_HEADERS)

    def page(self, url):
        response = self.client.get(url, **INERTIA_HEADERS)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_create_redirects_with_flash(self):
        response = self.post_json(
            "/budget/my-requests/new/", {"title": "Desk", "amount": 250.5, "justification": "Ergonomics"}
        )
        self.assertRedirects(response, "/budget/my-requests/", fetch_redirect_response=False)
        request = BudgetRequest.objects.get()
        self.assertEqual((request.title, str(request.amount)), ("Desk", "250.50"))

        page = self.page("/budget/my-requests/")
        self.assertEqual(page["component"], "Budget/MyRequests/Index")
        self.assertEqual(page["props"]["flash"], [{"level": "success", "message": 'Request "Desk" was submitted.'}])
        self.assertEqual(
            [item["route"] for item in page["props"]["budget_nav"]],
            ["budget_my_requests", "budget_request_create"],
        )

    def test_invalid_create_re_renders_form_with_input(self):
        response = self.post_json("/budget/my-requests/new/", {"title": "Desk", "amount": "abc"})
        page = response.json()
        self.assertEqual(page["component"], "Budget/MyRequests/Create")
        self.assertEqual(page["props"]["form"]["amount"], "abc")
        self.assertEqual(set(page["props"]["errors"]), {"amount", "justification"})
        self.assertFalse(BudgetRequest.objects.exists())

    def test_edit_and_failed_edit_of_a_reviewed_request(self):
        request = make_request(self.client_user)
        url = f"/budget/my-requests/{request.pk}/edit/"
        self.assertTrue(self.page(url)["props"]["editable"])

        BudgetRequest.objects.filter(pk=request.pk).update(status=Status.WITHDRAWN)
        page = self.post_json(url, {"title": "Changed", "amount": "1", "justification": "x"}).json()
        self.assertEqual(page["component"], "Budget/MyRequests/Edit")
        self.assertFalse(page["props"]["editable"])
        self.assertIn("non_field_errors", page["props"]["errors"])

    def test_withdraw_requires_post_and_flashes_the_outcome(self):
        request = make_request(self.client_user)
        url = f"/budget/my-requests/{request.pk}/withdraw/"
        self.assertEqual(self.client.get(url).status_code, 405)

        self.assertRedirects(self.client.post(url), "/budget/my-requests/", fetch_redirect_response=False)
        self.assertRedirects(self.client.post(url), "/budget/my-requests/", fetch_redirect_response=False)
        flash = self.page("/budget/my-requests/")["props"]["flash"]
        self.assertEqual([message["level"] for message in flash], ["success", "error"])

    def test_other_clients_requests_are_404(self):
        foreign = make_request(make_user("other", role=Role.CLIENT))
        self.assertEqual(self.client.get(f"/budget/my-requests/{foreign.pk}/edit/").status_code, 404)
        self.assertEqual(self.client.post(f"/budget/my-requests/{foreign.pk}/withdraw/").status_code, 404)


class ClientRouteProtectionTests(TestCase):
    def test_anonymous_users_are_sent_to_login(self):
        response = self.client.get("/budget/my-requests/")
        self.assertRedirects(response, "/admin/login/?next=/budget/my-requests/", fetch_redirect_response=False)

    def test_managers_and_admins_get_403_on_client_pages(self):
        request = make_request(make_user("client", role=Role.CLIENT))
        for role in (Role.MANAGER, Role.ADMIN):
            self.client.force_login(make_user(role.value, role=role))
            for method, url in (
                ("get", "/budget/my-requests/"),
                ("get", "/budget/my-requests/new/"),
                ("post", "/budget/my-requests/new/"),
                ("get", f"/budget/my-requests/{request.pk}/edit/"),
                ("post", f"/budget/my-requests/{request.pk}/withdraw/"),
            ):
                with self.subTest(role=role, method=method, url=url):
                    self.assertEqual(getattr(self.client, method)(url).status_code, 403)
        self.assertEqual(BudgetRequest.objects.get().status, Status.PENDING)
