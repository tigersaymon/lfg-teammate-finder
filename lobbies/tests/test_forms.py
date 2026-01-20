from django.test import TestCase

from games.models import Game, GameRole
from lobbies.forms import LobbyForm


class LobbyFormTest(TestCase):
    """Test suite for the Lobby creation form."""

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="CS2", slug="cs2", team_size=5)

        cls.role_sniper = GameRole.objects.create(
            game=cls.game,
            name="Sniper",
            order=1
        )
        cls.role_support = GameRole.objects.create(
            game=cls.game,
            name="Support",
            order=2
        )

        cls.other_game = Game.objects.create(
            title="Dota 2",
            slug="dota2",
            team_size=5
        )
        cls.other_role = GameRole.objects.create(
            game=cls.other_game,
            name="Mid",
            order=1
        )

    def test_form_initialization_filters_roles(self):
        """
        Verifies that the form only shows roles belonging to the passed game.
        """
        form = LobbyForm(game=self.game)

        host_role_queryset = form.fields["host_role"].queryset
        self.assertIn(self.role_sniper, host_role_queryset)
        self.assertIn(self.role_support, host_role_queryset)
        self.assertNotIn(self.other_role, host_role_queryset)

        needed_roles_queryset = form.fields["needed_roles"].queryset
        self.assertIn(self.role_sniper, needed_roles_queryset)
        self.assertNotIn(self.other_role, needed_roles_queryset)

    def test_form_sets_size_attributes(self):
        """
        Verifies that the form sets min/max/value attributes for size
        based on the game's team size.
        """
        form = LobbyForm(game=self.game)

        widget_attrs = form.fields["size"].widget.attrs

        self.assertEqual(widget_attrs["min"], 2)
        self.assertEqual(widget_attrs["max"], 10)
        self.assertEqual(widget_attrs["value"], 5)

    def test_valid_form_submission(self):
        """Verifies that the form accepts valid data."""
        form_data = {
            "title": "Valid Lobby",
            "description": "Lets play",
            "size": 5,
            "is_public": True,
            "host_role": self.role_sniper.id,
            "needed_roles": [self.role_support.id],
            "communication_link": "https://discord.gg/test"
        }
        form = LobbyForm(data=form_data, game=self.game)
        self.assertTrue(form.is_valid())

    def test_clean_size_validation(self):
        """
        Verifies that clean_size prevents creating a lobby larger than allowed.
        Max allowed is game.team_size * 2 (so 10 for CS2).
        """
        form_data = {
            "title": "Huge Lobby",
            "size": 11,
            "is_public": True
        }
        form = LobbyForm(data=form_data, game=self.game)

        self.assertFalse(form.is_valid())
        self.assertIn("size", form.errors)
        self.assertIn("Too many players", form.errors["size"][0])

    def test_roles_from_other_game_are_invalid(self):
        """
        Verifies that submitting a role ID from a different game raises a validation error.
        """
        form_data = {
            "title": "Hacker Lobby",
            "size": 5,
            "is_public": True,
            "host_role": self.other_role.id
        }
        form = LobbyForm(data=form_data, game=self.game)

        self.assertFalse(form.is_valid())
        self.assertIn("host_role", form.errors)
