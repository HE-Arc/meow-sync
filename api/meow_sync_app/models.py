from django.db import models  # noqa: F401
from django.conf import settings


MUSIC_PROVIDERS = {
        'spotify': 'Spotify',
        'youtube': 'Youtube',
}

class AbstractBaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class OAuthConnection(AbstractBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    provider = models.CharField(max_length=255, choices=MUSIC_PROVIDERS)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    extra_data = models.JSONField()

class OAuthState(AbstractBaseModel):
    "Used to keep track of user on OAuth callback."
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    state = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=255, choices=MUSIC_PROVIDERS)

class PlaylistSynchronization(AbstractBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    first_playlist_id = models.CharField(max_length=255)
    first_provider = models.CharField(max_length=255, choices=MUSIC_PROVIDERS)
    second_playlist_id = models.CharField(max_length=255)
    second_provider = models.CharField(max_length=255, choices=MUSIC_PROVIDERS)

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

    class Meta:
        unique_together = [
            ('user', 'youtube_id'),
            ('user', 'spotify_id'),
        ]

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
