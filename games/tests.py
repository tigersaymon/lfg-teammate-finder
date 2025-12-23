from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.forms import UserGameProfileForm
from games.models import Game, GameRole, UserGameProfile

User = get_user_model()


class GameFormTest(TestCase):
    """
    Tests for UserGameProfileForm logic, including dynamic queryset filtering
    and HTMX data handling.
    """

    @classmethod
    def setUpTestData(cls):
        cls.game_cs = Game.objects.create(title="CS2", slug="cs2", team_size=5)
        cls.game_dota = Game.objects.create(title="Dota 2", slug="dota-2", team_size=5)

        cls.role_sniper = GameRole.objects.create(game=cls.game_cs, name="Sniper", order=1)
        cls.role_support = GameRole.objects.create(game=cls.game_dota, name="Support", order=1)

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="Bob", password="StrongPass123")

    def test_form_excludes_existing_games(self) -> None:
        """
        Verifies that games already added to the user's profile are excluded
        from the 'game' selection dropdown.
        """
        UserGameProfile.objects.create(user=self.user, game=self.game_cs, rank="Gold")

        form = UserGameProfileForm(user=self.user)

        available_games = list(form.fields["game"].queryset)
        self.assertNotIn(self.game_cs, available_games)
        self.assertIn(self.game_dota, available_games)

    def test_form_populates_roles_based_on_game_data(self) -> None:
        """
        Verifies that passing a 'game' ID in data (HTMX simulation)
        correctly filters the 'main_role' queryset.
        """
        data = {"game": self.game_cs.id}
        form = UserGameProfileForm(data=data, user=self.user)

        role_queryset = form.fields["main_role"].queryset
        self.assertIn(self.role_sniper, role_queryset)
        self.assertNotIn(self.role_support, role_queryset)


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
