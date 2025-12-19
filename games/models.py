from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Game(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    icon = models.ImageField(
        upload_to="games/icons/",
        blank=True,
        null=True
    )

    team_size = models.PositiveIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20)
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Game"
        ordering = ["title"]

    def __str__(self):
        return self.title


class GameRole(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=1)

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="roles"
    )

    class Meta:
        ordering = ["game", "order"]
        constraints = [
            models.UniqueConstraint(fields=["game", "name"], name="unique_game_roles")
        ]

    def __str__(self):
        return f"{self.game.title} - {self.name}"
