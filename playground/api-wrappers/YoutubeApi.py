from dotenv import load_dotenv
from flask import redirect
import requests
from ApiInterface import ApiInterface, ApiResponse, ApiPlaylist, ApiSong
from typing import Any


class YoutubeApi(ApiInterface):
    API_BASE_URL = "https://www.googleapis.com/youtube/v3"
    def __init__(self, access_token):
        self.HEADERS = {
            "Authorization": f"Bearer {access_token}"
        }
        super().__init__()

    def search_song(self, query: str):
        pass

    def _parse_playlist(self, apiPlaylist: dict) -> ApiPlaylist:
        return ApiPlaylist(
            playlist_id=apiPlaylist['id'],
            title=apiPlaylist['snippet']['title'],
            description=apiPlaylist['snippet']['description'],
            author=apiPlaylist['snippet']['channelTitle'],
            image_url=apiPlaylist['snippet']['thumbnails']['default']['url'] if apiPlaylist['snippet']['thumbnails'] and apiPlaylist['snippet']['thumbnails']['default'] else None,
            songs=[]
        )

    def _parse_song(self, apiSong: dict) -> ApiSong:
        return ApiSong(
            song_id=apiSong['id'],
            title=apiSong['snippet']['title'],
            artist=apiSong['snippet']['videoOwnerChannelTitle'],
            image_url=apiSong['snippet']['thumbnails']['default']['url'] if apiSong['snippet']['thumbnails'] and apiSong['snippet']['thumbnails']['default'] else None,
            release_date=apiSong['contentDetails']['videoPublishedAt'],
            duration_ms=0  # Too much work for too low utility
        )
    
    def get_all_playlists(self) -> ApiResponse[list[ApiPlaylist]]:
        
        response = requests.get(f"{self.API_BASE_URL}/playlists?mine=true&part=snippet,contentDetails&maxResults=50", headers=self.HEADERS)
        result: list[ApiPlaylist] = []
        # Invalid JSON error
        try:
            data = response.json()
        except:
            return ApiResponse[list[ApiPlaylist]](
                success=False,
                message="Error parsing response JSON",
                status_code=response.status_code,
                data=response.text
            )

        # Spotify API error
        if response.status_code != 200:
            return ApiResponse[list[ApiPlaylist]](
                success=False,
                message=data['error']['message'],
                status_code=response.status_code,
                data=[]
            )

        # Happy case

        for playlist in data['items']:
            result.append(self._parse_playlist(playlist))
        
        return ApiResponse[list[ApiPlaylist]](
            success=True,
            message="",
            status_code=response.status_code,
            data=result
        )
    
    def _get_playlist_info(self, playlist_id: str) -> ApiResponse:
        response = requests.get(f"{self.API_BASE_URL}/playlists?part=snippet,contentDetails&maxResults=50&id={playlist_id}", headers=self.HEADERS)

        # Invalid JSON error
        try:
            data = response.json()
        except:
            raise Exception("Error parsing response JSON")

        # Spotify API error
        if response.status_code != 200:
            raise Exception(data['error']['message'] if data['error'] and data['error']['message'] else "Youtube Api Error")
        
        return ApiResponse(
            success=True,
            message="",
            status_code=response.status_code,
            data=self._parse_playlist(data['items'][0])
        )

    def get_playlist(self, playlist_id: Any) -> ApiResponse[ApiPlaylist]:
        song_page_url = f"{self.API_BASE_URL}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}"
        playlist_info = self._get_playlist_info(playlist_id)
        result = playlist_info.data

        # Invalid JSON error
        
        songs: list[ApiSong] = []
        next_page_token = ""
        while True:
            response = requests.get(song_page_url + next_page_token, headers=self.HEADERS)
            try:
                data = response.json()
            except:
                return ApiResponse[list[ApiPlaylist]](
                    success=False,
                    message="Error parsing response JSON",
                    status_code=response.status_code,
                    data=response.text
                )

            # Spotify API error
            if response.status_code != 200:
                return ApiResponse[list[ApiPlaylist]](
                    success=False,
                    message=data['error']['message'],
                    status_code=response.status_code,
                    data=[]
                )

            # Happy case
            for song in data['items']:
                songs.append(self._parse_song(song))

            if not data.get('nextPageToken'):
                break
            next_page_token = f"&pageToken={data['nextPageToken']}"

        result.songs = songs
        
        return ApiResponse[list[ApiPlaylist]](
            success=True,
            message="",
            status_code=response.status_code,
            data=result
        )

    def add_to_playlist(self, playlist_id: Any, song_ids: list[Any]) -> ApiResponse:
        pass
    def remove_from_playlist(self, playlist_id: Any, song_ids: list[Any]) -> ApiResponse:
        pass
    def create_playlist(self, title: ApiPlaylist) -> ApiResponse[ApiPlaylist]:
        pass