from django.test import TestCase

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.tests.factories import make_request, make_user
from apps.users.selectors.roles import Role

INERTIA_HEADERS = {"HTTP_X_INERTIA": "true", "HTTP_X_INERTIA_VERSION": "1.0"}


class AdminOverviewViewTests(TestCase):
    def setUp(self):
        self.client.force_login(make_user("admin", role=Role.ADMIN))
        self.request = make_request(make_user("alice", role=Role.CLIENT), title="Team offsite")

    def test_overview_page(self):
        page = self.client.get("/budget/overview/?status=PENDING", **INERTIA_HEADERS).json()
        self.assertEqual(page["component"], "Budget/Overview/Index")
        self.assertEqual(page["props"]["status"], "PENDING")
        self.assertEqual([r["id"] for r in page["props"]["requests"]], [self.request.pk])

    def test_delete_removes_the_request_and_keeps_the_filter(self):
        response = self.client.post(
            f"/budget/overview/{self.request.pk}/delete/",
            '{"status": "PENDING"}',
            content_type="application/json",
            **INERTIA_HEADERS,
        )
        self.assertRedirects(response, "/budget/overview/?status=PENDING", fetch_redirect_response=False)
        self.assertFalse(BudgetRequest.objects.exists())

        page = self.client.get(response["Location"], **INERTIA_HEADERS).json()
        self.assertEqual(page["props"]["flash"][0]["message"], 'Request "Team offsite" was permanently deleted.')
        self.assertEqual(page["props"]["summary"]["total"]["count"], 0)

    def test_delete_works_for_decided_requests(self):
        decided = make_request(make_user("bob", role=Role.CLIENT), status=Status.APPROVED)
        response = self.client.post(f"/budget/overview/{decided.pk}/delete/")
        self.assertRedirects(response, "/budget/overview/", fetch_redirect_response=False)
        self.assertFalse(BudgetRequest.objects.filter(pk=decided.pk).exists())

    def test_deleting_a_missing_request_is_404(self):
        self.assertEqual(self.client.post("/budget/overview/999999/delete/").status_code, 404)

    def test_delete_requires_post(self):
        self.assertEqual(self.client.get(f"/budget/overview/{self.request.pk}/delete/").status_code, 405)
        self.assertTrue(BudgetRequest.objects.exists())


class OverviewRouteProtectionTests(TestCase):
    def test_clients_and_managers_get_403(self):
        request = make_request(make_user("alice", role=Role.CLIENT))
        for role in (Role.CLIENT, Role.MANAGER):
            self.client.force_login(make_user(f"u-{role.value}", role=role))
            with self.subTest(role=role):
                self.assertEqual(self.client.get("/budget/overview/").status_code, 403)
                self.assertEqual(self.client.post(f"/budget/overview/{request.pk}/delete/").status_code, 403)
        self.assertTrue(BudgetRequest.objects.filter(pk=request.pk).exists())

    def test_anonymous_users_are_sent_to_login(self):
        response = self.client.get("/budget/overview/")
        self.assertRedirects(response, "/admin/login/?next=/budget/overview/", fetch_redirect_response=False)
