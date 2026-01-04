from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.models import Game, GameRole, UserGameProfile

User = get_user_model()


class GameViewTests(TestCase):
    """
    Tests for Views, focusing on HTMX responses and access permissions.
    """

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="Valorant", slug="valorant", team_size=5)
        cls.role = GameRole.objects.create(game=cls.game, name="Duelist", order=1)

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="gamer",
            email="gamer@example.com",
            password="password"
        )
        self.other_user = User.objects.create_user(
            username="hacker",
            email="hacker@example.com",
            password="AnotherStrongPass12"
        )
        self.client.force_login(self.user)

    def test_htmx_get_game_roles(self) -> None:
        """
        Verifies that the HTMX view returns correct <option> tags
        for the selected game.
        """
        url = reverse("games:get-game-roles")
        response = self.client.get(url, {"game": self.game.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Duelist")
        self.assertContains(response, f'value="{self.role.id}"')

    def test_update_view_security(self) -> None:
        """
        Verifies that a user cannot access the update page for
        another user's game profile.
        """
        url = reverse("games:profile-edit", kwargs={"game_slug": self.game.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_create_profile_assigns_current_user(self) -> None:
        """
        Verifies that the CreateView automatically assigns the
        logged-in user to the new profile.
        """
        url = reverse("games:profile-create")
        data = {
            "game": self.game.id,
            "rank": "Silver",
            "main_role": self.role.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(UserGameProfile.objects.filter(user=self.user, game=self.game).exists())
