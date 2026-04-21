from django.contrib import admin  # noqa: F401
from .models import (
	OAuthConnection,
	OAuthState,
	PlaylistSynchronization,
	SongIdTranslation,
	Comment,
)

admin.site.register(OAuthConnection)
admin.site.register(OAuthState)
admin.site.register(PlaylistSynchronization)
admin.site.register(SongIdTranslation)
admin.site.register(Comment)
