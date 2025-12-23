from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.models import Game, GameRole, UserGameProfile
from lobbies.models import Lobby

User = get_user_model()


class LobbyCreateTest(TestCase):
    """
    Tests for Lobby creation logic, including prerequisites and slot generation.
    """

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="CS2", slug="cs2", team_size=5)
        cls.role = GameRole.objects.create(game=cls.game, name="Sniper", order=1)

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass12"
        )
        self.profile = UserGameProfile.objects.create(
            user=self.user, game=self.game, rank="Global"
        )

    def test_user_cannot_create_lobby_without_profile(self):
        """Verify redirect to profile creation if user has no game profile."""
        no_profile_user = User.objects.create_user(
            username="noob",
            email="noob@example.com",
            password="NoobPass2"
        )
        self.client.force_login(no_profile_user)

        url = reverse("lobbies:lobby-create", kwargs={"game_slug": self.game.slug})
        response = self.client.get(url)

        self.assertRedirects(response, reverse("games:profile-create"))

    def test_create_lobby_generates_slots_automatically(self):
        """
        Verify that creating a Lobby automatically generates 'team_size' slots
        and assigns the host to the first slot.
        """
        self.client.force_login(self.user)
        url = reverse("lobbies:lobby-create", kwargs={"game_slug": self.game.slug})

        data = {
            "title": "Test Lobby",
            "description": "For testing purposes",
            "size": 5,
            "is_public": True,
            "communication_link": "",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        lobby = Lobby.objects.get(title="Test Lobby")
        self.assertEqual(lobby.host, self.user)

        self.assertEqual(lobby.slots.count(), 5)

        first_slot = lobby.slots.get(order=1)
        self.assertEqual(first_slot.player, self.user)


class LobbyVisibilityTests(TestCase):
    """
    Tests for LobbyListView filtering logic (Public vs Private).
    """

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="Dota 2", slug="dota2", team_size=5)

    def setUp(self):
        self.host = User.objects.create_user(
            username="host",
            email="host@ex.com",
            password="pw"
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@ex.com",
            password="pw"
        )
        UserGameProfile.objects.create(user=self.host, game=self.game, rank="Immortal")

        self.private_lobby = Lobby.objects.create(
            title="Private Room",
            game=self.game,
            host=self.host,
            is_public=False,
            size=5
        )

    def test_private_lobby_hidden_for_others(self):
        """Private lobbies should not appear in the list for non-members."""
        self.client.force_login(self.other)
        url = reverse("lobbies:lobby-list", kwargs={"game_slug": self.game.slug})

        response = self.client.get(url)

        self.assertNotContains(response, "Private Room")

    def test_private_lobby_visible_for_host(self):
        """Host should always see their own private lobby."""
        self.client.force_login(self.host)
        url = reverse("lobbies:lobby-list", kwargs={"game_slug": self.game.slug})

        response = self.client.get(url)

        self.assertContains(response, "Private Room")


class SlotActionTests(TestCase):
    """
    Tests for joining, leaving, and kicking logic.
    """

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(title="Valorant", slug="val", team_size=5)

    def setUp(self):
        self.host = User.objects.create_user(
            username="host",
            email="h@ex.com",
            password="pw"
        )
        UserGameProfile.objects.create(user=self.host, game=self.game, rank="Radiant")

        self.player = User.objects.create_user(
            username="player",
            email="p@ex.com",
            password="pw"
        )
        UserGameProfile.objects.create(user=self.player, game=self.game, rank="Gold")

        self.lobby = Lobby.objects.create(
            title="Ranked", game=self.game, host=self.host, size=5
        )

        self.slot_2 = self.lobby.slots.get(order=2)

    def test_join_slot_success(self):
        """User with profile can join an empty slot."""
        self.client.force_login(self.player)

        url = reverse("lobbies:lobby-join", kwargs={
            "game_slug": self.game.slug,
            "invite_link": self.lobby.invite_link,
            "slot_id": self.slot_2.id
        })

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.slot_2.refresh_from_db()
        self.assertEqual(self.slot_2.player, self.player)

    def test_host_cannot_leave_lobby(self):
        """Host attempts to leave their slot -> Error."""
        self.client.force_login(self.host)
        host_slot = self.lobby.slots.get(order=1)

        url = reverse("lobbies:lobby-leave", kwargs={
            "game_slug": self.game.slug,
            "invite_link": self.lobby.invite_link,
            "slot_id": host_slot.id
        })

        response = self.client.post(url)

        host_slot.refresh_from_db()
        self.assertEqual(host_slot.player, self.host)

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("host cannot leave" in str(m) for m in messages))

    def test_kick_player_permission(self):
        """Only host can kick players."""
        self.slot_2.player = self.player
        self.slot_2.save()

        other_user = User.objects.create_user(
            username="random",
            email="r@ex.com",
            password="pw"
        )
        self.client.force_login(other_user)

        url = reverse("lobbies:lobby-kick", kwargs={
            "game_slug": self.game.slug,
            "invite_link": self.lobby.invite_link,
            "slot_id": self.slot_2.id
        })

        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        self.client.force_login(self.host)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.slot_2.refresh_from_db()
        self.assertIsNone(self.slot_2.player)
