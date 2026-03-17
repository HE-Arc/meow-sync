from rest_framework import serializers
from .models import UserPlaylist


class UserPlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlaylist
        fields = '__all__'
