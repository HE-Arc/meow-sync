from rest_framework import viewsets
from .models import UserPlaylist
from .serializers import UserPlaylistSerializer


class UserPlaylistViewSet(viewsets.ModelViewSet):
	queryset = UserPlaylist.objects.all()
	serializer_class = UserPlaylistSerializer
