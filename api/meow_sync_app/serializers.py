from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
	Comment,
	MusicProvider,
	OAuthConnection,
	PlaylistSynchronization,
	SongIdTranslation,
)


class CommentSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField(read_only=True)

	class Meta:
		model = Comment
		fields = ['id', 'comment', 'user', 'playlist_sync', 'created_at', 'updated_at']
		read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PlaylistSynchronizationSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField(read_only=True)
	first_provider = serializers.ChoiceField(choices=MusicProvider.values)
	second_provider = serializers.ChoiceField(choices=MusicProvider.values)

	def validate(self, data):
		if data['first_provider'] == data['second_provider']:
			raise serializers.ValidationError('Providers must be different')
		return data

	class Meta:
		model = PlaylistSynchronization
		fields = [
			'id',
			'user',
			'first_playlist_id',
			'first_provider',
			'second_playlist_id',
			'second_provider',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SongIdTranslationSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField(read_only=True)

	class Meta:
		model = SongIdTranslation
		fields = [
			'id',
			'user',
			'spotify_id',
			'youtube_id',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class OAuthLoginResponseSerializer(serializers.Serializer):
	provider = serializers.ChoiceField(choices=tuple(MusicProvider.values))
	state = serializers.CharField()
	login_url = serializers.URLField()


class OAuthCallbackSuccessSerializer(serializers.Serializer):
	message = serializers.CharField()
	auth_token = serializers.CharField()


class OAuthMessageSerializer(serializers.Serializer):
	message = serializers.CharField()


class OAuthConnectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = OAuthConnection
		fields = ['provider', 'provider_user_id']
		read_only_fields = fields


class MeSerializer(serializers.ModelSerializer):
	connections = OAuthConnectionSerializer(
		many=True, read_only=True, source='oauthconnection_set'
	)

	class Meta:
		model = User
		fields = [
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'date_joined',
			'connections',
		]
		read_only_fields = fields


class SearchSerializer(serializers.Serializer):
	q = serializers.CharField(required=True, help_text='Search query term')


class ApiSongSerializer(serializers.Serializer):
	id = serializers.CharField(help_text='song ID')
	title = serializers.CharField(help_text='Song title')
	artist = serializers.CharField(help_text='Artist name')
	image_url = serializers.URLField(allow_null=True, help_text='Image URL')
	release_date = serializers.DateTimeField(help_text='Publish date')
	duration_ms = serializers.IntegerField(help_text='Duration of the song in milliseconds', required=False)


class SearchResponseSerializer(serializers.Serializer):
	data = ApiSongSerializer(many=True)
	message = serializers.CharField()

class ApiPlaylistSerializer(serializers.Serializer):
	id = serializers.CharField(help_text='playlist ID')
	title = serializers.CharField(help_text='playlist title')
	description = serializers.CharField(help_text='playlist description')
	author = serializers.CharField(help_text='playlist author')
	image_url = serializers.URLField(allow_null=True, help_text='Image URL')
	songs = ApiSongSerializer(many=True)


class ProviderPlaylistsResponseSerializer(serializers.Serializer):
	data = ApiPlaylistSerializer(many=True)
	message = serializers.CharField()
