from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    avatar = CloudinaryField(
        "avatar",
        folder="avatars",
        blank=True,
        null=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    discord_tag = models.CharField(max_length=100, blank=True)
    steam_url = models.URLField(blank=True)
    reputation = models.IntegerField(default=0)

    games = models.ManyToManyField(
        "games.Game",
        through="games.UserGameProfile",
        related_name="players",
        blank=True
    )

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username
