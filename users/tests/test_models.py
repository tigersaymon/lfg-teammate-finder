from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test suite for the custom User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser",
            email="test@example.com",
            password="password123"
        )

    def test_user_string_representation(self):
        """Verifies that the __str__ method returns the username."""
        self.assertEqual(str(self.user), "TestUser")

    def test_email_is_unique(self):
        """Verifies that creating a user with a duplicate email raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="AnotherUser",
                email="test@example.com",  # Duplicate email
                password="password123"
            )

    def test_reputation_default_value(self):
        """Verifies that the reputation field defaults to 0."""
        self.assertEqual(self.user.reputation, 0)

    def test_custom_fields_creation(self):
        """Verifies that custom fields (bio, discord_tag, steam_url) can be saved."""
        self.user.bio = "Pro gamer"
        self.user.discord_tag = "gamer#1234"
        self.user.steam_url = "https://steamcommunity.com/id/gamer"
        self.user.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Pro gamer")
        self.assertEqual(self.user.discord_tag, "gamer#1234")
