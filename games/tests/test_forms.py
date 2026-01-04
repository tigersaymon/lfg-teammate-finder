from django.contrib.auth import get_user_model
from django.test import TestCase

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
