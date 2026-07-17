from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve

from .forms import CustomUserCreationForm
from .views import SignupPageView

#Create all tests here

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
    def setUp(self):
        self.url = reverse("signup")
    
    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "registration/signup.html")
        self.assertContains(self.response, "Sign Up")
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_signup_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, CustomUserCreationForm)
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_signup_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.view_class, SignupPageView)
    
    def test_signup_form_creates_user_and_redirects(self):
        # 1. Verify the user doesn't exist yet
        self.assertFalse(
            get_user_model().objects.filter(username="newuser").exists()
        )
        # 2. Submit valid registration data
        response = self.client.post(
            self.url,
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
        )
        # 3. Assert it redirects to the login page (or your custom success URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

        # 4. Assert the user was successfully written to the database
        self.assertTrue(
            get_user_model().objects.filter(username="newuser").exists()
        )