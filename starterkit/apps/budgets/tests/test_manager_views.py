import json

from django.test import TestCase

from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.tests.factories import make_request, make_user
from apps.users.selectors.roles import Role

INERTIA_HEADERS = {"HTTP_X_INERTIA": "true", "HTTP_X_INERTIA_VERSION": "1.0"}


class ManagerViewTests(TestCase):
    def setUp(self):
        self.manager = make_user("manager", role=Role.MANAGER)
        self.client.force_login(self.manager)
        self.request = make_request(make_user("alice", role=Role.CLIENT))
        self.url = f"/budget/review/{self.request.pk}/"

    def post_json(self, data):
        return self.client.post(self.url, json.dumps(data), content_type="application/json", **INERTIA_HEADERS)

    def reload(self):
        return BudgetRequest.objects.get(pk=self.request.pk)

    def test_queue_page(self):
        page = self.client.get("/budget/review/?tab=pending", **INERTIA_HEADERS).json()
        self.assertEqual(page["component"], "Budget/Review/Index")
        self.assertEqual([r["id"] for r in page["props"]["requests"]], [self.request.pk])

    def test_approve_redirects_back_to_the_tab_with_flash(self):
        response = self.post_json({"decision": "APPROVED", "note": "", "tab": "pending"})
        self.assertRedirects(response, "/budget/review/?tab=pending", fetch_redirect_response=False)
        self.assertEqual(self.reload().status, Status.APPROVED)

        page = self.client.get(response["Location"], **INERTIA_HEADERS).json()
        self.assertEqual(page["props"]["requests"], [])
        self.assertEqual(page["props"]["flash"][0]["message"], 'Request "New laptops" was approved.')

    def test_reject_without_note_re_renders_the_review_page(self):
        page = self.post_json({"decision": "REJECTED", "note": "  "}).json()
        self.assertEqual(page["component"], "Budget/Review/Show")
        self.assertIn("note", page["props"]["errors"])
        self.assertEqual(page["props"]["form"]["decision"], "REJECTED")
        self.assertEqual(self.reload().status, Status.PENDING)

    def test_second_review_shows_that_the_decision_is_final(self):
        self.post_json({"decision": "REJECTED", "note": "Too much"})
        page = self.post_json({"decision": "APPROVED", "note": ""}).json()
        self.assertEqual(page["component"], "Budget/Review/Show")
        self.assertIn("non_field_errors", page["props"]["errors"])
        self.assertFalse(page["props"]["request"]["can"]["review"])
        self.assertEqual(self.reload().status, Status.REJECTED)


class ReviewRouteProtectionTests(TestCase):
    def test_clients_and_admins_cannot_open_or_use_the_queue(self):
        request = make_request(make_user("alice", role=Role.CLIENT))
        for role in (Role.CLIENT, Role.ADMIN):
            self.client.force_login(make_user(role.value, role=role))
            for method, url in (
                ("get", "/budget/review/"),
                ("get", f"/budget/review/{request.pk}/"),
                ("post", f"/budget/review/{request.pk}/"),
            ):
                with self.subTest(role=role, method=method, url=url):
                    response = getattr(self.client, method)(url, {"decision": "APPROVED"} if method == "post" else None)
                    self.assertEqual(response.status_code, 403)
        self.assertEqual(BudgetRequest.objects.get().status, Status.PENDING)

    def test_anonymous_users_are_sent_to_login(self):
        response = self.client.get("/budget/review/")
        self.assertRedirects(response, "/admin/login/?next=/budget/review/", fetch_redirect_response=False)
