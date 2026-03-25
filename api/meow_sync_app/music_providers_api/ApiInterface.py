from typing import Any, Generic, TypeVar

T = TypeVar("T")

class ApiSong:
    def __init__(self, song_id, title: str, artist: str, image_url: str|None, release_date: str, duration_ms: int, id_in_playlist: str|None = None):
        self.id = song_id
        self.title: str = title
        self.artist: str = artist
        self.image_url: str|None = image_url
        self.release_date: str = release_date
        self.duration_ms: int = duration_ms

        # Specific to delete a video in a Youtube playlist, a new id is created when a video is added to a playlist.
        # So we need to keep track of it if we want to delete the video from the playlist later
        self.id_in_playlist: str = id_in_playlist 
    
    def get_formatted_duration(self):
        total_seconds = self.duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{int(minutes)}:{int(seconds):02d}"

class ApiPlaylist:
    def __init__(self, playlist_id: Any,  title: str, description: str|None, author: str, image_url:str|None, songs: list[ApiSong]|None):
        self.id: Any = playlist_id
        self.title: str = title
        self.description: str|None = description
        self.author: str = author
        self.image_url: str|None = image_url
        self.songs: list[ApiSong]|None = songs

class ApiUser:
    def __init__(self, name: str, user_id: str):
        self.name = name
        self.id = user_id

class ApiTokens:
    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in

class ApiResponse(Generic[T]):
    def __init__(self, success: bool, message: str, status_code: int, data: T):
        self.success: bool = success
        self.message: str = message
        self.status_code: int = status_code
        self.data: T = data

class ApiInterface:
    @classmethod
    def login_url(self, state: str) -> str:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')
    
    @classmethod
    def get_tokens(self, code: str) -> ApiTokens:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')

    def __init__(self, access_token: str):
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')

    def get_current_user(self) -> ApiResponse[ApiUser]:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')

    def search_song(self, query: str):
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')

    def get_all_playlists(self) -> ApiResponse[list[ApiPlaylist]]:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')
    def get_playlist(self, playlist_id: Any) -> ApiResponse[ApiPlaylist]:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')

    def add_to_playlist(self, playlist_id: Any, song_ids: list[Any]) -> ApiResponse:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')
    def add_to_playlist_single(self, playlist_id: str, song_id: str) -> ApiResponse:
        return self.add_to_playlist(playlist_id, [song_id])
        
    def remove_from_playlist(self, playlist_id: Any, song_ids: list[Any]) -> ApiResponse:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')
    def remove_from_playlist_single(self, playlist_id: str, song_id: str) -> ApiResponse:
        return self.remove_from_playlist(playlist_id, [song_id])

    def create_playlist(self, title: ApiPlaylist) -> ApiResponse[ApiPlaylist]:
        raise ValueError('Method not implemented, this is an abstract class ApiInterface')
