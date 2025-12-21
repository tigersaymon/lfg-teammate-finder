import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class Lobby(models.Model):
    class Status(models.TextChoices):
        SEARCHING = "SE", _("Searching")
        IN_PROGRESS = "IP", _("In progress")
        COMPLETED = "CO", _("Completed")
        CANCELLED = "CA", _("Canceled")

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.SEARCHING,
    )

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    size = models.PositiveIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20)
        ]
    )

    invite_link = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_lobbies"
    )

    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="lobbies"
    )

    class Meta:
        verbose_name = "Lobby"
        verbose_name_plural = "Lobbies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.game.title})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_new:
                self._create_slots()

    def _create_slots(self):
        slots = []

        for i in range(1, self.size + 1):
            slots.append(Slot(lobby=self, order=i))

        Slot.objects.bulk_create(slots)

        first_slot = self.slots.get(order=1)
        first_slot.player = self.host
        first_slot.save()

    def get_invite_url(self):
        return f"/lobbies/join/{self.invite_link}/"

    def can_join(self, user):
        if self.status != self.Status.SEARCHING:
            return False, "Lobby is not accepting players"

        if self.is_full:
            return False, "Lobby is full"

        if self.slots.filter(player=user).exists():
            return False, "You are already in this lobby"

        return True, "OK"

    @property
    def filled_count(self):
        return self.slots.filter(player__isnull=False).count()

    @property
    def is_full(self):
        return self.filled_count >= self.size


class Slot(models.Model):
    order = models.PositiveIntegerField()
    joined_at = models.DateTimeField(null=True, blank=True)

    lobby = models.ForeignKey(
        Lobby,
        on_delete=models.CASCADE,
        related_name="slots"
    )

    required_role = models.ForeignKey(
        "games.GameRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="slots"
    )

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="occupied_slots"
    )

    class Meta:
        ordering = ["lobby", "order"]
        constraints = [
            models.UniqueConstraint(fields=["lobby", "order"], name="unique_slot_positions"),
            models.UniqueConstraint(fields=["lobby", "player"], name="unique_player_per_lobby"),
        ]

    def __str__(self):
        role_str = self.required_role.name if self.required_role else "Any"
        player_str = self.player.username if self.player else "Empty"
        return f"Slot {self.order}: {player_str} ({role_str})"

    def save(self, *args, **kwargs):
        from django.utils import timezone

        if self.player and not self.joined_at:
            self.joined_at = timezone.now()
        elif not self.player:
            self.joined_at = None

        super().save(*args, **kwargs)

        if self.lobby.status == Lobby.Status.SEARCHING and self.lobby.is_full:
            self.lobby.status = Lobby.Status.IN_PROGRESS
            self.lobby.save(update_fields=["status"])

    @property
    def is_filled(self):
        return self.player is not None

    @property
    def is_available(self):
        return self.player is None

    @property
    def role_name(self):
        return self.required_role.name if self.required_role else "Any Role"

    @property
    def role_icon(self):
        return self.required_role.icon_class if self.required_role else "fa-solid fa-users"
