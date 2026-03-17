from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserPlaylist
from .serializers import UserPlaylistSerializer

@api_view(['GET'])
def getData(request):
    playlists = UserPlaylist.objects.all()
    serializer = UserPlaylistSerializer(playlists, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getUserPlaylist(request, pk):
    playlists = UserPlaylist.objects.get(id=pk)
    serializer = UserPlaylistSerializer(playlists, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def addUserPlaylist(request):
    serializer = UserPlaylistSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['PUT'])
def updateUserPlaylist(request, pk):
    playlist = UserPlaylist.objects.get(id=pk)
    serializer = UserPlaylistSerializer(instance=playlist, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['DELETE'])
def deleteUserPlaylist(request, pk):
    playlist = UserPlaylist.objects.get(id=pk)
    playlist.delete()
    return Response('Playlist successfully deleted!')

