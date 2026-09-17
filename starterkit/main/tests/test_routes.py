from django.test import SimpleTestCase
from django.urls import reverse

from main.routes import EXPOSED_ROUTE_NAMES, route_map


class RouteMapTests(SimpleTestCase):
    def test_every_exposed_route_resolves(self):
        routes = route_map()
        self.assertEqual(set(routes), set(EXPOSED_ROUTE_NAMES))

    def test_placeholders_match_reverse(self):
        routes = route_map()
        self.assertEqual(routes["admin_users"], reverse("admin_users"))
        self.assertEqual(
            routes["admin_user_edit"].replace("{user_id}", "42"),
            reverse("admin_user_edit", kwargs={"user_id": 42}),
        )
