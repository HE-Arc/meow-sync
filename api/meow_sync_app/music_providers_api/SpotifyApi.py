import os
import requests
from dotenv import load_dotenv

from .ApiInterface import *

load_dotenv()

class SpotifyApi(ApiInterface):
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE_URL = "https://api.spotify.com/v1"
    REDIRECT_URI = "https://https://meow.k8s.ing.he-arc.ch/api/oauth/callback"

    @classmethod
    def login_url(state: str) -> str:
        scope = "playlist-read-private,playlist-read-collaborative,playlist-modify-public,playlist-modify-private"

        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "scope": scope,
            "redirect_uri": REDIRECT_URI,
            "state": state,
        }

        return requests.Request("GET", AUTH_URL, params=params).prepare().url

    @classmethod
    def get_tokens(code: str) -> ApiTokens:
        auth_header = base64.b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
        ).decode()

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }

        token_headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(TOKEN_URL, data=token_data, headers=token_headers)
        token_info = response.json()

        access_token = token_info["access_token"]
        refresh_token = token_info["refresh_token"]
        expires_in = token_info["expires_in"]

        return ApiTokens(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)

    def __init__(self, access_token: str):
        self.HEADERS = {
            "Authorization": f"Bearer {access_token}"
        }
        self.MAX_SONG_CHUNK_SIZE = 100

    def get_current_user(self) -> ApiResponse[ApiUser]:
        CURRENT_USER_URL = f'{self.API_BASE_URL}/me'

        current_user_response = requests.get(request_url, headers=self.HEADERS)

        # Spotify API error
        if playlist_response.status_code != 200:
            return ApiResponse[ApiUser](
                success=False,
                message=data['error']['message'],
                status_code=playlist_response.status_code,
                data=None
            )

        try:
            data = playlist_response.json()

            return ApiResponse[ApiUser](
                success=True,
                message="",
                status_code=playlist_response.status_code,
                data=ApiUser(name=data['display_name'], user_id=data['id'])
            )

        except:
            return ApiResponse[list[ApiPlaylist]](
                success=False,
                message="Error parsing response JSON",
                status_code=playlist_response.status_code,
                data=playlist_response.text
            )

    def get_all_playlists(self) -> ApiResponse[list[ApiPlaylist]]:
        current_page_url = f"{self.API_BASE_URL}/me/playlists"
        result: list[ApiPlaylist] = []
        while True:
            playlist_response = requests.get(current_page_url, headers=self.HEADERS)
            # Invalid JSON error
            try:
                data = playlist_response.json()
            except:
                return ApiResponse[list[ApiPlaylist]](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=playlist_response.status_code,
                    data=playlist_response.text
                )

            # Spotify API error
            if playlist_response.status_code != 200:
                return ApiResponse[list[ApiPlaylist]](
                    success=False,
                    message=data['error']['message'],
                    status_code=playlist_response.status_code,
                    data=[]
                )

            # Happy case
            for playlist in data['items']:
                songs: list[ApiSong] = []

                result.append(ApiPlaylist(
                    playlist_id=playlist['id'],
                    title=playlist['name'],
                    description=playlist['description'],
                    author=playlist['owner']['display_name'],
                    image_url=playlist['images'][0]['url'] if playlist['images'] and playlist['images'][0] else None,
                    songs=songs
                ))
            
            if not data['next']:
                break
            current_page_url = data['next']
            
        
        return ApiResponse[list[ApiPlaylist]](
            success=True,
            message="",
            status_code=playlist_response.status_code,
            data=result
        )

    def _get_playlist_info(self, playlist_id: str) -> ApiPlaylist:
        request_url = f"{self.API_BASE_URL}/playlists/{playlist_id}"

        playlist_response = requests.get(request_url, headers=self.HEADERS)

        data = playlist_response.json()

        # Spotify API error
        if playlist_response.status_code != 200:
            raise Exception(f"{data['error']['message']}, status_code: {playlist_response.status_code}")
        
        # Happy case
        result = ApiPlaylist(
            playlist_id=data['id'],
            title=data['name'],
            description=data['description'],
            author=data['owner']['display_name'],
            image_url=data['images'][0]['url'] if data['images'] and data['images'][0] else None,
            songs=[]
        )

        return result

    
    def get_playlist(self, playlist_id: str) -> ApiResponse[ApiPlaylist]:
        songs = []
        current_song_page_url = f"{self.API_BASE_URL}/playlists/{playlist_id}/items"

        try:
            result = self._get_playlist_info(playlist_id)
        except Exception as ex:
            return ApiResponse[ApiPlaylist](
                success=False,
                message=ex.message,
                status_code=0,
                data=None
            )

        # get playlist songs
        while True:
            playlist_songs_response = requests.get(current_song_page_url, headers=self.HEADERS)
            # Invalid JSON error
            try:
                data = playlist_songs_response.json()
            except:
                return ApiResponse[ApiPlaylist](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=playlist_songs_response.status_code,
                    data=None
                )

            # Spotify API error
            if playlist_songs_response.status_code != 200:
                return ApiResponse[ApiPlaylist](
                    success=False,
                    message=data['error']['message'] if data['message'] else "Spotify Api Error",
                    status_code=playlist_songs_response.status_code,
                    data=None
                )
            
            # Happy case
            for song in data['items']:
                song_data = song['item']
                songs.append(ApiSong(
                    song_id=song_data['id'],
                    title=song_data['name'],
                    artist=', '.join(artist['name'] for artist in song_data['artists']),
                    image_url=song_data['album']['images'][0]['url'] if song_data['album']['images'] and song_data['album']['images'][0] else None,
                    release_date=song_data['album']['release_date'],
                    duration_ms=song_data['duration_ms']
                ))
            if not data['next']:
                break
            current_song_page_url = data['next']

        result.songs = songs

        return ApiResponse(
            success=True,
            message="",
            status_code=200,
            data=result
        )
    
    def _song_id_to_uri(self, song_ids: list[str]):
        prefix = "spotify:track:"
        result = list(map(lambda song : prefix + song, song_ids))

        return result

    def _chunk_list(self, lst: list, chunk_size: int):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    def add_to_playlist(self, playlist_id: str, song_ids: list[str]) -> ApiResponse[None]:
        chunked_ids = self._chunk_list(song_ids, self.MAX_SONG_CHUNK_SIZE)
        
        for chunk in chunked_ids:
            request_url = f"{self.API_BASE_URL}/playlists/{playlist_id}/items"
            
            request_body = {
                "uris": self._song_id_to_uri(chunk)
            }

            response = requests.post(request_url, json=request_body, headers=self.HEADERS)
            
            try:
                data = response.json()
            except:
                return ApiResponse[None](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=response.status_code,
                    data=None
                )

            # Spotify API error
            if response.status_code != 201:
                return ApiResponse[None](
                    success=False,
                    message=data['error']['message'],
                    status_code=response.status_code,
                    data=None
                )
        
        return ApiResponse(
            success=True,
            message="Successfully added songs to playlist",
            status_code=response.status_code,
            data=None
        )
    
    def remove_from_playlist(self, playlist_id: str, song_ids: list[str]) -> ApiResponse[None]:
        chunked_ids = self._chunk_list(song_ids, self.MAX_SONG_CHUNK_SIZE)
        
        for chunk in chunked_ids:
            request_url = f"{self.API_BASE_URL}/playlists/{playlist_id}/items"
            
            request_body = {
                "items": [ { 'uri': uri } for uri in self._song_id_to_uri(chunk) ]
            }

            response = requests.delete(request_url, json=request_body, headers=self.HEADERS)
            
            try:
                data = response.json()
            except:
                return ApiResponse[None](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=response.status_code,
                    data=None
                )

            # Spotify API error
            if response.status_code != 200:
                return ApiResponse[None](
                    success=False,
                    message=data['error']['message'],
                    status_code=response.status_code,
                    data=None
                )

        # Happy case
        return ApiResponse[None](
            success=True,
            message="Successfully removed songs from playlist",
            status_code=200,
            data=None
        )
    
    def create_playlist(self, playlist: ApiPlaylist) -> ApiResponse[ApiPlaylist]:
        request_url = f"{self.API_BASE_URL}/me/playlists"
        PLAYLIST_PUBLIC = False
        PLAYLIST_COLLABORATIVE = False

        request_body = {
            'name': playlist.title,
            'description': playlist.description,
            'collaborative': PLAYLIST_COLLABORATIVE,
            'public': PLAYLIST_PUBLIC,
        }

        response = requests.post(request_url, json=request_body, headers=self.HEADERS)

        # Json error
        try:
            data = response.json()
        except:
            return ApiResponse[None](
                success=False,
                message="Failed to parse JSON",
                status_code=response.status_code,
                data=None
            )

        # Spotify API error
        if response.status_code != 201:
            return ApiResponse[None](
                success=False,
                message="Spotify API Error",
                status_code=response.status_code,
                data=None
            )
        
        playlist.author = data['owner']['display_name']
        playlist.id = data['id']
        playlist.songs = []

        # Happy case
        return ApiResponse[ApiPlaylist](
            success=True,
            message="Successfully created playlist",
            status_code=response.status_code,
            data=playlist
        )

    def search_song(self, query: str):
        # TODO
        pass
