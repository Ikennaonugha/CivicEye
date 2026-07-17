from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve

from django_project import settings


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="will", email="will@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "will")
        self.assertEqual(user.email, "will@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
class SignUpPageTests(TestCase):
    username = "newuser"
    email = "newuser@email.com"
    
    def setUp(self):
        self.url = reverse("account_signup")
        self.response = self.client.get(self.url)
    
    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign Up")
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")
    
    def test_signup_form_creates_user_and_redirects(self):
        # Verify the user doesn't exist yet
        self.assertFalse(
            get_user_model().objects.filter(username=self.username).exists()
        )
        # Submit valid registration data using allauth field specs
        response = self.client.post(
            self.url,
            data={
                "username": self.username,
                "email": self.email,
                "password1": "securepassword123",
                "password2": "securepassword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        
        # to LOGIN_REDIRECT_URL instead of the login screen.
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

        # Assert the user was successfully written to the database
        self.assertTrue(
            get_user_model().objects.filter(username=self.username).exists()
        )