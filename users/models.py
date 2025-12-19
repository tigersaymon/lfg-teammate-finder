from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/%d/",
        blank=True,
        null=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    discord_tag = models.CharField(max_length=100, blank=True)
    steam_url = models.URLField(blank=True)
    reputation = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username
