from typing import Any, Generic, TypeVar

T = TypeVar("T")

class ApiSong:
    def __init__(self, song_id, title: str, artist: str, image_url: str|None, release_date: str, duration_ms: int):
        self.id = song_id
        self.title: str = title
        self.artist: str = artist
        self.image_url: str|None = image_url
        self.release_date: str = release_date
        self.duration_ms: int = duration_ms

class ApiPlaylist:
    def __init__(self, playlist_id: Any,  title: str, description: str|None, author: str, image_url:str|None, songs: list[ApiSong]|None):
        self.id: Any = playlist_id
        self.title: str = title
        self.description: str|None = description
        self.author: str = author
        self.image_url: str|None = image_url
        self.songs: list[ApiSong]|None = songs

class ApiResponse(Generic[T]):
    def __init__(self, success: bool, message: str, status_code: int, data: T):
        self.success: bool = success
        self.message: str = message
        self.status_code: int = status_code
        self.data: T = data

class ApiInterface:
    def search_song(self, query: str):
        raise ValueError('Method not implemented')
    def get_all_playlists(self) -> ApiResponse[list[ApiPlaylist]]:
        raise ValueError('Method not implemented')
    def get_playlist(self, playlist_id: Any) -> ApiResponse[ApiPlaylist]:
        raise ValueError('Method not implemented')
    def add_to_playlist(self, playlist: ApiPlaylist, song: ApiSong) -> ApiResponse:
        raise ValueError('Method not implemented')
    def remove_from_playlist(self, playlist: ApiPlaylist, song: ApiSong) -> ApiResponse:
        raise ValueError('Method not implemented')
    def create_playlist(self, title: str, author: str) -> ApiResponse:
        raise ValueError('Method not implemented')
    def delete_playlist(self, playlist: ApiPlaylist) -> ApiResponse:
        raise ValueError('Method not implemented')