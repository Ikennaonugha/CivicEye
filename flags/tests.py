from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from captcha.conf import settings as captcha_settings
from captcha.models import CaptchaStore
from flags.models import ProcurementProject, CivicFlag

User = get_user_model()


@override_settings(CAPTCHA_TEST_MODE=True)
class FlagReportingWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Force captcha package settings into test mode
        captcha_settings.CAPTCHA_TEST_MODE = True

    def setUp(self):
        # Create test project with required fields
        self.project = ProcurementProject.objects.create(
            title="Lagos-Ikorodu Road Rehabilitation",
            contract_id="LAG-PROCUR-2026-001",
            description="Rehabilitation of critical section on Ikorodu road.",
            lga="Ikorodu",
            state="Lagos",
            contractor="BuildMore Ltd",
            budget=150000000.00,
        )
        # Create test user
        self.user = User.objects.create_user(
            username="citizen_auditor",
            email="auditor@civiceye.ng",
            password="Password123!"
        )
        self.submit_url = reverse("flags:submit_flag", kwargs={"project_id": self.project.id})

    def _get_captcha_payload(self, response_text="passed"):
        """Generate valid captcha key and answer for test forms."""
        key = CaptchaStore.generate_key()
        return {
            "captcha_0": key,
            "captcha_1": response_text,
        }

    def test_invalid_project_id_returns_404(self):
        """Requesting flag submission for a non-existent project_id returns 404."""
        invalid_url = reverse("flags:submit_flag", kwargs={"project_id": 999999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_captcha_validation_failure(self):
        """Submitting a flag with an invalid CAPTCHA answer fails form validation."""
        post_data = {
            "issue_type": "delay",
            "headline": "No activity on site",
            "description": "Site has been empty for over 3 months.",
            **self._get_captcha_payload(response_text="wrong_answer"),
        }
        response = self.client.post(self.submit_url, post_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "captcha", "Invalid CAPTCHA")
        self.assertEqual(CivicFlag.objects.count(), 0)

    def test_anonymous_guest_flag_submission_and_ip_capture(self):
        """Anonymous guest user can submit a flag with valid CAPTCHA and IP address captured."""
        post_data = {
            "issue_type": "delay",
            "headline": "Project delayed beyond deadline",
            "description": "Completion target passed with no updates.",
            **self._get_captcha_payload("passed"),
        }
        response = self.client.post(self.submit_url, post_data, REMOTE_ADDR="197.210.8.12")

        self.assertIn(response.status_code, [301, 302])
        
        flag = CivicFlag.objects.get(project=self.project)
        self.assertIsNone(flag.user)
        self.assertEqual(flag.headline, "Project delayed beyond deadline")
        self.assertEqual(flag.ip_address, "197.210.8.12")

    def test_authenticated_user_flag_attribution(self):
        """Authenticated user submission correctly attributes user account to the flag."""
        self.client.login(username="citizen_auditor", password="Password123!")
        
        post_data = {
            "issue_type": "quality",
            "headline": "Substandard asphalt thickness",
            "description": "The newly laid asphalt is already washing away after rain.",
            **self._get_captcha_payload("passed"),
        }
        response = self.client.post(self.submit_url, post_data)

        self.assertIn(response.status_code, [301, 302])
        
        flag = CivicFlag.objects.get(project=self.project)
        self.assertEqual(flag.user, self.user)
        self.assertEqual(flag.headline, "Substandard asphalt thickness")

    def test_guest_submission_rate_limit(self):
        """Multiple submissions from the same IP address enforce guest submission limits (max 2)."""
        base_payload = {
            "issue_type": "other",
            "headline": "Test repeated flag",
            "description": "Testing IP limit behavior.",
        }

        # 1st Submission (Allowed)
        p1 = {**base_payload, **self._get_captcha_payload("passed")}
        res1 = self.client.post(self.submit_url, p1, REMOTE_ADDR="10.0.0.1")
        self.assertIn(res1.status_code, [301, 302])
        self.assertEqual(CivicFlag.objects.filter(ip_address="10.0.0.1").count(), 1)

        # 2nd Submission (Allowed)
        p2 = {**base_payload, **self._get_captcha_payload("passed")}
        res2 = self.client.post(self.submit_url, p2, REMOTE_ADDR="10.0.0.1")
        self.assertIn(res2.status_code, [301, 302])
        self.assertEqual(CivicFlag.objects.filter(ip_address="10.0.0.1").count(), 2)

        # 3rd Submission (Blocked by guest rate limit in view)
        p3 = {**base_payload, **self._get_captcha_payload("passed")}
        res3 = self.client.post(self.submit_url, p3, REMOTE_ADDR="10.0.0.1")
        self.assertEqual(res3.status_code, 200)  # Re-renders form without saving
        self.assertEqual(CivicFlag.objects.filter(ip_address="10.0.0.1").count(), 2)