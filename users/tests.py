from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthTest(TestCase):
    """Test suite for user registration and authentication logic."""

    def setUp(self) -> None:
        self.signup_url = reverse("users:sign-up")
        self.user_data = {
            "username": "Bob",
            "email": "bob@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }

    def test_sign_up_successful(self) -> None:
        """Verifies that a user can register with valid data."""
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="Bob").exists())

    def test_signup_duplicate_email_fails(self) -> None:
        """Verifies that the custom clean_email validation prevents duplicate emails."""
        User.objects.create_user(username="new_bob", email="bob@example.com", password="password")
        response = self.client.post(self.signup_url, self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "Email already exists")


class UserSettingTest(TestCase):
    """Test suite for user profile management features."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="CoolBob",
            email="settings@example.com",
            password="ComplexPass123!"
        )
        self.settings_url = reverse("settings-general")
        self.client.login(username="CoolBob", password="ComplexPass123!")

    def test_settings_page_requires_login(self) -> None:
        """Verifies that unauthenticated users are redirected to login."""
        self.client.logout()
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_settings_update_successful(self) -> None:
        """Verifies that a user can update their bio and discord tag."""
        updated_data = {
            "username": "SuperBob",
            "email": "settings@example.com", # Disabled but sent in post
            "bio": "New awesome bio",
            "discord_tag": "user#1111"
        }
        response = self.client.post(self.settings_url, updated_data)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.bio, "New awesome bio")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile updated successfully!")

    def test_email_field_is_read_only(self) -> None:
        """Verifies that email cannot be changed through the settings form."""
        initial_email = self.user.email
        updated_data = {
            "username": "CoolBob",
            "email": "hacker@example.com",
            "bio": "Hacker bio"
        }
        self.client.post(self.settings_url, updated_data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, initial_email)
