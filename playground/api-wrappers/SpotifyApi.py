import os
import requests
from dotenv import load_dotenv

from ApiInterface import ApiInterface, ApiResponse, ApiPlaylist, ApiSong

load_dotenv()

class SpotifyApi(ApiInterface):
    API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    def get_all_playlists(self) -> ApiResponse[list[ApiPlaylist]]:
        current_page_url = f"{self.API_BASE_URL}/me/playlists"
        result: list[ApiPlaylist] = []
        while True:
            playlist_response = requests.get(current_page_url, headers=self.headers)
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
                print(playlist_response.status_code)
                return ApiResponse[list[ApiPlaylist]](
                    success=False,
                    message=data['message'],
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
    
    def get_playlist(self, playlist_id: str) -> ApiResponse[ApiPlaylist]:
        songs = []
        current_page_url = f"{self.API_BASE_URL}/playlists/{playlist_id}"

        # To set playlist data - Playlist data exists only on first api call
        first_pass = True
        result = None
        while True:
            playlist_response = requests.get(current_page_url, headers=self.headers)
            # Invalid JSON error
            try:
                data = playlist_response.json()
                print(data['items']['next'])
            except:
                return ApiResponse[ApiPlaylist](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=playlist_response.status_code,
                    data=None
                )

            # Spotify API error
            if playlist_response.status_code != 200:
                return ApiResponse[ApiPlaylist](
                    success=False,
                    message=data['message'],
                    status_code=playlist_response.status_code,
                    data=None
                )
            # User cannot access playlist
            if not data['items']:
                return ApiResponse[ApiPlaylist](
                    success=False,
                    message="You do not have access to this playlist.",
                    status_code=playlist_response.status_code,
                    data=None
                )
            
            # Happy case
            if first_pass:
                # Playlist data exists only on first api call
                print('setting playlist')
                result = ApiPlaylist(
                    playlist_id=data['id'],
                    title=data['name'],
                    description=data['description'],
                    author=data['owner']['display_name'],
                    image_url=data['images'][0]['url'] if data['images'] and data['images'][0] else None,
                    songs=[]
                )
                first_pass = False

            for song in data['items']['items']:
                song_data = song['item']
                songs.append(ApiSong(
                    song_id=song_data['id'],
                    title=song_data['name'],
                    artist=', '.join(artist['name'] for artist in song_data['artists']),
                    image_url=song_data['album']['images'][0]['url'] if song_data['album']['images'] and song_data['album']['images'][0] else None,
                    release_date=song_data['album']['release_date'],
                    duration_ms=song_data['duration_ms']
                ))
            # TODO: paginated results do not work, must investigate
            print(data['items']['next'])
            break
            if not data['items']['next']:
                break
            current_page_url = data['items']['next']

        result.songs = songs

        return ApiResponse(
            success=True,
            message="",
            status_code=playlist_response.status_code,
            data=result
        )