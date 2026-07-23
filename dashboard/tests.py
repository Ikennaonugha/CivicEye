from django.test import TestCase
from django.urls import reverse


class DashboardHomeTests(TestCase):
    def test_dashboard_home_returns_ok(self):
        response = self.client.get(reverse("dashboard_home"))
        self.assertEqual(response.status_code, 200)