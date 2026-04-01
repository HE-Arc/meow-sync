from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Comment, MusicProvider, OAuthConnection


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = '__all__'


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
