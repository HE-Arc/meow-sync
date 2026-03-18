from django.db import models
from django.conf import settings
from meow_sync_app.models import AbstractBaseModel, MUSIC_PROVIDERS


class UserPlaylist(AbstractBaseModel):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
	)
	playlist_id = models.CharField(max_length=255)
	provider = models.CharField(max_length=255, choices=MUSIC_PROVIDERS)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	author = models.CharField(max_length=255)
	img_url = models.CharField(max_length=255, blank=True, null=True)
