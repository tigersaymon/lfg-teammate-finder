from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Game(models.Model):
    """
    Represents a video game supported by the platform.

    This model serves as the core configuration for each supported title,
    storing branding elements and technical constraints like team size,
    which is used to automate lobby and slot generation.
    """
    title = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    icon = CloudinaryField(
        "game_icon",
        folder="games/icons/",
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
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class GameRole(models.Model):
    """
    Defines specific playable roles for a Game (e.g., 'Sniper', 'Healer').

    Roles allow for more structured matchmaking by letting users indicate
    their preferred position or allowing lobby hosts to request specific needs.
    """
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

    def __str__(self) -> str:
        return self.name


class UserGameProfile(models.Model):
    """
    Stores user-specific gaming metadata for a particular Game.

    Acts as a 'digital player card', linking a User to a Game with
    additional info like their rank and primary role. This data is
    essential for entering lobbies.
    """
    rank = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_profiles"
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="user_profiles"
    )

    main_role = models.ForeignKey(
        GameRole,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="main_user_role"
    )

    class Meta:
        verbose_name = "Game Profile"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_profiles")
        ]

    def __str__(self) -> str:
        return f"{self.user.username} in {self.game.title}"
