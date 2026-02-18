from typing import Any

class ApiSong:
    def __init__(self, song_id, title: str, artist: str, image_url: str, release_date: str):
        self.id = song_id
        self.title: str = title
        self.artist: str = artist
        self.image_url: str = image_url
        self.release_date: str = release_date

class ApiPlaylist:
    def __init__(self, playlist_id: Any,  title: str, author: str, songs: list[ApiSong]):
        self.playlist_id: Any = playlist_id
        self.title: str = title
        self.author: str = author
        self.songs: list[ApiSong] = songs

class ApiResponse:
    def __init__(self, success: bool, message: str, status_code: int, data: Any):
        self.success: bool = success
        self.message: str = message
        self.status_code: int = status_code
        self.data: Any = data

class ApiInterface:
    def search_song(self, query: str):
        pass
    def get_all_playlists(self) -> ApiResponse:
        pass
    def get_playlist(self, playlist: ApiPlaylist) -> ApiResponse:
        pass
    def add_to_playlist(self, playlist: ApiPlaylist, song: ApiSong) -> ApiResponse:
        pass
    def remove_from_playlist(self, playlist: ApiPlaylist, song: ApiSong) -> ApiResponse:
        pass
    def create_playlist(self, title: str, author: str) -> ApiResponse:
        pass
    def delete_playlist(self, playlist: ApiPlaylist) -> ApiResponse:
        pass