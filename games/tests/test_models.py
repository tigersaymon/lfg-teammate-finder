from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from games.models import Game, GameRole, UserGameProfile

User = get_user_model()


class GameModelTest(TestCase):
    """Test suite for the Game model."""

    def test_string_representation(self):
        """Verifies that the string representation is the game title."""
        game = Game.objects.create(
            title="Apex Legends",
            slug="apex",
            team_size=3
        )
        self.assertEqual(str(game), "Apex Legends")


class GameRoleModelTest(TestCase):
    """Test suite for the GameRole model."""

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(
            title="Overwatch",
            slug="overwatch",
            team_size=5
        )

    def test_string_representation(self):
        """Verifies that the string representation is the role name."""
        role = GameRole.objects.create(game=self.game, name="Tank")
        self.assertEqual(str(role), "Tank")

    def test_unique_role_per_game_constraint(self):
        """Verifies that role names must be unique within a single game."""
        GameRole.objects.create(game=self.game, name="DPS")

        with self.assertRaises(IntegrityError):
            GameRole.objects.create(game=self.game, name="DPS")


class UserGameProfileModelTest(TestCase):
    """Test suite for the UserGameProfile model."""

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="CS2", slug="cs2", team_size=5)
        cls.user = User.objects.create_user(
            username="Player1",
            password="password"
        )

    def test_string_representation(self):
        """Verifies the string representation format."""
        profile = UserGameProfile.objects.create(
            user=self.user,
            game=self.game,
            rank="Global"
        )
        self.assertEqual(str(profile), "Player1 in CS2")

    def test_unique_profile_per_game_constraint(self):
        """Verifies that a user can have only one profile per game."""
        UserGameProfile.objects.create(
            user=self.user,
            game=self.game,
            rank="Silver"
        )

        with self.assertRaises(IntegrityError):
            UserGameProfile.objects.create(
                user=self.user,
                game=self.game,
                rank="Gold"
            )
