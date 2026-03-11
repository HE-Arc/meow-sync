from django.db import models  # noqa: F401
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass
    spotify_token = models.TextField(blank=True)
    youtube_token = models.TextField(blank=True)

    def __str__(self):
        return self.username
