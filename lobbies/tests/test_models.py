from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from games.models import Game, GameRole
from lobbies.models import Lobby

User = get_user_model()


class LobbyModelTest(TestCase):
    """Test suite for Lobby model logic (creation, slots generation, status)."""

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(
            title="Test Game",
            slug="test-game",
            team_size=5
        )
        cls.host = User.objects.create_user(
            username="host",
            email="host@test.com",
            password="password"
        )

    def test_lobby_creation_generates_slots(self):
        """Verifies that creating a Lobby automatically creates 'size' number of slots."""
        lobby = Lobby.objects.create(
            title="Auto Slots Test",
            game=self.game,
            host=self.host,
            size=3
        )

        self.assertEqual(lobby.slots.count(), 3)

        first_slot = lobby.slots.get(order=1)
        self.assertEqual(first_slot.player, self.host)

        second_slot = lobby.slots.get(order=2)
        self.assertIsNone(second_slot.player)

    def test_can_join_logic(self):
        """Verifies the can_join method returns correct boolean and reason."""
        lobby = Lobby.objects.create(
            title="Join Logic Test", game=self.game, host=self.host, size=3
        )

        new_user = User.objects.create_user(
            username="newbie",
            email="newbie@test.com",
            password="password"
        )

        can_join, reason = lobby.can_join(new_user)
        self.assertTrue(can_join)
        self.assertEqual(reason, "OK")

        slot_2 = lobby.slots.get(order=2)
        slot_2.player = new_user
        slot_2.save()

        can_join, reason = lobby.can_join(new_user)
        self.assertFalse(can_join)
        self.assertEqual(reason, "You are already in this lobby")

        filler_user = User.objects.create_user(
            username="filler", email="filler@test.com", password="pw"
        )
        slot_3 = lobby.slots.get(order=3)
        slot_3.player = filler_user
        slot_3.save()

        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="password"
        )

        lobby.status = Lobby.Status.SEARCHING
        lobby.save()

        can_join, reason = lobby.can_join(other_user)
        self.assertFalse(can_join)
        self.assertEqual(reason, "Lobby is full")

    def test_lobby_is_full_property(self):
        """Verifies is_full property works correctly."""
        lobby = Lobby.objects.create(game=self.game, host=self.host, size=1)
        self.assertTrue(lobby.is_full)

        lobby_big = Lobby.objects.create(
            game=self.game,
            host=self.host,
            size=5
        )
        self.assertFalse(lobby_big.is_full)


class SlotModelTest(TestCase):
    """Test suite for Slot model logic."""

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(
            title="Test Game",
            slug="test-game",
            team_size=5
        )
        cls.role = GameRole.objects.create(
            game=cls.game,
            name="Healer",
            order=1
        )
        cls.host = User.objects.create_user(
            username="host",
            email="host@test.com",
            password="password"
        )

    def setUp(self):
        self.lobby = Lobby.objects.create(
            title="Slot Test",
            game=self.game,
            host=self.host,
            size=2
        )
        self.slot_2 = self.lobby.slots.get(order=2)
        self.player = User.objects.create_user(
            username="player",
            email="player@test.com",
            password="password"
        )

    def test_slot_auto_updates_joined_at(self):
        """Verifies joined_at timestamp is set when a player is assigned."""
        self.assertIsNone(self.slot_2.joined_at)

        self.slot_2.player = self.player
        self.slot_2.save()

        self.assertIsNotNone(self.slot_2.joined_at)

    def test_slot_clears_joined_at_on_leave(self):
        """Verifies joined_at is cleared when player leaves."""
        self.slot_2.player = self.player
        self.slot_2.save()

        self.slot_2.player = None
        self.slot_2.save()

        self.assertIsNone(self.slot_2.joined_at)

    def test_lobby_status_update_on_full(self):
        """Verifies lobby status changes to IN_PROGRESS when last slot is filled."""
        self.assertEqual(self.lobby.status, Lobby.Status.SEARCHING)

        self.slot_2.player = self.player
        self.slot_2.save()

        self.lobby.refresh_from_db()
        self.assertEqual(self.lobby.status, Lobby.Status.IN_PROGRESS)

    def test_unique_player_constraint(self):
        """Verifies database constraint: A player cannot occupy two slots in the same lobby."""
        slot_2 = self.lobby.slots.get(order=2)
        slot_2.player = self.host

        with self.assertRaises(IntegrityError):
            slot_2.save()
