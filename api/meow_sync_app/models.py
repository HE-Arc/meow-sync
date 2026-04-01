from django.db import models  # noqa: F401
from django.conf import settings


class MusicProvider(models.TextChoices):
	SPOTIFY = 'spotify', 'Spotify'
	YOUTUBE = 'youtube', 'Youtube'


class AbstractBaseModel(models.Model):
	id = models.BigAutoField(primary_key=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class OAuthConnection(AbstractBaseModel):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	provider_user_id = models.CharField(max_length=255)
	provider = models.CharField(max_length=255, choices=MusicProvider.choices)
	access_token = models.CharField(max_length=255)
	refresh_token = models.CharField(max_length=255)
	token_expires_at = models.DateTimeField()
	extra_data = models.JSONField(null=True)


class OAuthState(AbstractBaseModel):
	"Used to keep track of user on OAuth callback."

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
	state = models.CharField(max_length=255, unique=True)
	provider = models.CharField(max_length=255, choices=MusicProvider.choices)


class PlaylistSynchronization(AbstractBaseModel):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	first_playlist_id = models.CharField(max_length=255)
	first_provider = models.CharField(max_length=255, choices=MusicProvider.choices)
	second_playlist_id = models.CharField(max_length=255)
	second_provider = models.CharField(max_length=255, choices=MusicProvider.choices)

	commenters = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		through='Comment',
		related_name='commented_playlist_syncs',
	)


class SongIdTranslation(AbstractBaseModel):
	# optional, for user specific overrides
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)

	spotify_id = models.CharField(max_length=255, blank=True, null=True)
	youtube_id = models.CharField(max_length=255, blank=True, null=True)

	class Meta(AbstractBaseModel.Meta):
		unique_together = [
			('user', 'youtube_id'),
			('user', 'spotify_id'),
		]


class Comment(AbstractBaseModel):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='playlist_sync_comment',
	)
	playlist_sync = models.ForeignKey(
		PlaylistSynchronization,
		on_delete=models.CASCADE,
		related_name='comment',
	)
	comment = models.TextField()

	class Meta(AbstractBaseModel.Meta):
		ordering = ['-created_at']
