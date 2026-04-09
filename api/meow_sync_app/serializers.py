from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Comment, MusicProvider, OAuthConnection, PlaylistSynchronization


class CommentSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField(read_only=True)

	class Meta:
		model = Comment
		fields = ['id', 'comment', 'user', 'playlist_sync', 'created_at', 'updated_at']
		read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PlaylistSynchronizationSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField(read_only=True)
	first_provider = serializers.ChoiceField(choices=MusicProvider.choices)
	second_provider = serializers.ChoiceField(choices=MusicProvider.choices)

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
