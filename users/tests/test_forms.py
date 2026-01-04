from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import SignUpForm, UserSettingsForm

User = get_user_model()


class SignUpFormTest(TestCase):
    """Test suite for the registration form."""

    def test_email_field_is_required(self):
        """Verifies that the email field is required."""
        form = SignUpForm(data={
            "username": "testuser",
            "password": "password123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_clean_email_enforces_uniqueness(self):
        """Verifies that the custom clean_email method enforces uniqueness."""
        User.objects.create_user(username="first", email="exists@test.com",
                                 password="pwd")

        form = SignUpForm(data={
            "username": "second",
            "email": "exists@test.com",
            "password": "pwd"
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "Email already exists")


class UserSettingsFormTest(TestCase):
    """Test suite for the profile settings form."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser",
                                             email="my@email.com",
                                             password="pwd")

    def test_email_field_is_disabled(self):
        """Verifies logic in __init__: the email field must be disabled."""
        form = UserSettingsForm(instance=self.user)

        self.assertTrue(form.fields["email"].disabled)

        self.assertIn("bg-light", form.fields["email"].widget.attrs["class"])
        self.assertIn("text-muted", form.fields["email"].widget.attrs["class"])

    def test_form_updates_allowed_fields(self):
        """Verifies that allowed fields (bio, discord) are updated successfully."""
        form_data = {
            "username": "testuser",
            "email": "hacker@email.com",
            "bio": "New Bio",
            "discord_tag": "new#1234",
            "steam_url": ""
        }
        form = UserSettingsForm(data=form_data, instance=self.user)

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.email, "my@email.com")
        self.assertEqual(user.bio, "New Bio")
