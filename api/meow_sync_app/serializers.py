# from .models import *


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ["url", "username", "email", "groups"]

from rest_framework import serializers
from .models import Comment, MUSIC_PROVIDERS


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = '__all__'


class OAuthLoginResponseSerializer(serializers.Serializer):
	provider = serializers.ChoiceField(choices=tuple(MUSIC_PROVIDERS.keys()))
	state = serializers.CharField()
	login_url = serializers.URLField()


class OAuthCallbackSuccessSerializer(serializers.Serializer):
	message = serializers.CharField()
	# auth_token = serializers.CharField()


class OAuthMessageSerializer(serializers.Serializer):
	message = serializers.CharField()
