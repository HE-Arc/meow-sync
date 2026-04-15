import os

import requests
from .ApiInterface import (
	ApiInterface,
	ApiSuccess,
	ApiError,
	ApiUser,
	ApiTokens,
	ApiPlaylist,
	ApiSong,
	ApiSearchQuery,
)
from typing import Any


class YoutubeApi(ApiInterface):
	CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
	CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
	REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI')

	AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
	TOKEN_URL = 'https://oauth2.googleapis.com/token'
	API_BASE_URL = 'https://www.googleapis.com/youtube/v3'

	@classmethod
	def login_url(cls, state: str) -> str:
		scope = 'https://www.googleapis.com/auth/youtube'

		# access_type
		auth_params = {
			'state': state,
			'response_type': 'code',
			'client_id': cls.CLIENT_ID,
			'scope': scope,
			'redirect_uri': cls.REDIRECT_URI,
			'access_type': 'offline',
			'prompt': 'consent',
		}

		url = requests.Request('GET', cls.AUTH_URL, params=auth_params).prepare().url

		if not url:
			raise Exception('Failed to construct Youtube login URL')

		return url

	@classmethod
	def get_tokens(cls, code: str) -> ApiTokens:

		code = code
		id_client = cls.CLIENT_ID
		secret_client = cls.CLIENT_SECRET
		grant_type = 'authorization_code'
		redirect_uri = cls.REDIRECT_URI

		response = requests.post(
			cls.TOKEN_URL,
			data={
				'client_id': id_client,
				'client_secret': secret_client,
				'grant_type': grant_type,
				'code': code,
				'redirect_uri': redirect_uri,
			},
		)
		token_info = response.json()
		print(f'Token response: {token_info}')

		access_token = token_info['access_token']
		refresh_token = token_info['refresh_token']
		expires_in = token_info['expires_in']

		return ApiTokens(
			access_token=access_token,
			refresh_token=refresh_token,
			expires_in=expires_in,
		)

	def __init__(self, access_token):
		self.HEADERS = {'Authorization': f'Bearer {access_token}'}

	def get_current_user(self) -> ApiSuccess[ApiUser] | ApiError:
		CURRENT_USER_URL = f'{self.API_BASE_URL}/channels?part=snippet&mine=true'

		current_user_response = requests.get(CURRENT_USER_URL, headers=self.HEADERS)

		try:
			data = current_user_response.json()
		except Exception as e:
			print(f'Error parsing Youtube current user response JSON: {e}')
			return ApiError(
				status_code=current_user_response.status_code,
				message='Error parsing response JSON',
			)

		# Youtube API error
		if current_user_response.status_code != 200:
			return ApiError(
				status_code=current_user_response.status_code,
				message=data.get('error', {}).get('message', 'Youtube API Error'),
			)

		return ApiSuccess(
			status_code=current_user_response.status_code,
			data=ApiUser(
				name=data['items'][0]['snippet']['title'],
				user_id=data['items'][0]['id'],
			),
		)

	def _parse_playlist(self, apiPlaylist: dict) -> ApiPlaylist:
		return ApiPlaylist(
			playlist_id=apiPlaylist['id'],
			title=apiPlaylist['snippet']['title'],
			description=apiPlaylist['snippet']['description'],
			author=apiPlaylist['snippet']['channelTitle'],
			image_url=apiPlaylist['snippet']['thumbnails']['default']['url']
			if apiPlaylist['snippet']['thumbnails']
			and apiPlaylist['snippet']['thumbnails']['default']
			else None,
			songs=[],
		)

	def _parse_song(self, apiSong: dict) -> ApiSong:
		return ApiSong(
			song_id=apiSong['snippet']['resourceId']['videoId'],
			title=apiSong['snippet']['title'],
			artist=apiSong['snippet']['videoOwnerChannelTitle'],
			image_url=apiSong['snippet']['thumbnails']['default']['url']
			if apiSong['snippet']['thumbnails']
			and apiSong['snippet']['thumbnails']['default']
			else None,
			release_date=apiSong['contentDetails']['videoPublishedAt'],
			duration_ms=0,  # Too much work for too low utility
			id_in_playlist=apiSong['id'],
		)

	def get_all_playlists(self) -> ApiSuccess[list[ApiPlaylist]] | ApiError:

		response = requests.get(
			f'{self.API_BASE_URL}/playlists?mine=true&part=snippet,contentDetails&maxResults=50',
			headers=self.HEADERS,
		)
		result: list[ApiPlaylist] = []
		# Invalid JSON error
		try:
			data = response.json()
		except Exception as e:
			print(f'Error parsing Youtube playlists response JSON: {e}')
			return ApiError(
				status_code=response.status_code,
				message='Error parsing response JSON',
			)

		# Youtube API error
		if response.status_code != 200:
			return ApiError(
				status_code=response.status_code,
				message=data['error']['message'],
			)

		# Happy case
		for playlist in data['items']:
			result.append(self._parse_playlist(playlist))

		return ApiSuccess(status_code=response.status_code, data=result)

	def _get_playlist_info(self, playlist_id: str) -> ApiSuccess[ApiPlaylist]:
		response = requests.get(
			f'{self.API_BASE_URL}/playlists?part=snippet,contentDetails&maxResults=50&id={playlist_id}',
			headers=self.HEADERS,
		)

		# Invalid JSON error
		try:
			data = response.json()
		except Exception as e:
			print(f'Error parsing Youtube playlist info response JSON: {e}')
			raise Exception('Error parsing response JSON')

		# Youtube API error
		if response.status_code != 200:
			raise Exception(
				data['error']['message']
				if data['error'] and data['error']['message']
				else 'Youtube Api Error'
			)

		return ApiSuccess(
			status_code=response.status_code,
			data=self._parse_playlist(data['items'][0]),
		)

	def get_playlist(self, playlist_id: Any) -> ApiSuccess[ApiPlaylist] | ApiError:
		song_page_url = f'{self.API_BASE_URL}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}'
		try:
			playlist_info = self._get_playlist_info(playlist_id)
		except Exception as ex:
			return ApiError(status_code=500, message=str(ex))
		result = playlist_info.data

		songs: list[ApiSong] = []
		next_page_token = ''
		while True:
			response = requests.get(
				song_page_url + next_page_token, headers=self.HEADERS
			)
			try:
				data = response.json()
			except Exception as e:
				print(f'Error parsing Youtube playlist songs response JSON: {e}')
				return ApiError(
					status_code=response.status_code,
					message='Error parsing response JSON',
				)

			# Youtube API error
			if response.status_code != 200:
				return ApiError(
					status_code=response.status_code,
					message=data['error']['message'],
				)

			# Happy case
			for song in data['items']:
				songs.append(self._parse_song(song))

			if not data.get('nextPageToken'):
				break
			next_page_token = f'&pageToken={data["nextPageToken"]}'

		result.songs = songs

		return ApiSuccess(status_code=response.status_code, data=result)

	def add_to_playlist(
		self, playlist_id: str, song_ids: list[str]
	) -> ApiSuccess[None] | ApiError:
		for video_id in song_ids:
			request_url = (
				f'{self.API_BASE_URL}/playlistItems?part=snippet,contentDetails'
			)

			request_body = {
				'snippet': {
					'playlistId': playlist_id,
					'resourceId': {'videoId': video_id, 'kind': 'youtube#video'},
				}
			}

			response = requests.post(
				request_url, json=request_body, headers=self.HEADERS
			)

			try:
				_ = response.json()
			except Exception as e:
				print(f'Error parsing Youtube add to playlist response JSON: {e}')
				return ApiError(
					status_code=response.status_code,
					message='Error parsing response JSON',
				)

			# Youtube API error
			if response.status_code != 200:
				return ApiError(
					status_code=response.status_code,
					message=response.text,
				)

		return ApiSuccess(
			status_code=201,
			data=None,
			message='Successfully added songs to playlist',
		)

	def remove_from_playlist(
		self, playlist_id: str, song_ids: list[str]
	) -> ApiSuccess[None] | ApiError:
		for video_id in song_ids:
			request_url = f'{self.API_BASE_URL}/playlistItems?id={video_id}'

			response = requests.delete(request_url, headers=self.HEADERS)

			try:
				data = response.json()
			except Exception as e:
				print(f'Error parsing Youtube remove from playlist response JSON: {e}')
				return ApiError(
					status_code=response.status_code,
					message='Error parsing response JSON',
				)

			# Youtube API error
			if response.status_code != 204:
				return ApiError(
					status_code=response.status_code,
					message=data['error']['message'],
				)

		# Happy case
		return ApiSuccess(
			status_code=204,
			data=None,
			message='Successfully removed songs from playlist',
		)

	def create_playlist(
		self, playlist: ApiPlaylist
	) -> ApiSuccess[ApiPlaylist] | ApiError:
		PRIVACY_STATUS = 'private'
		response = requests.post(
			f'{self.API_BASE_URL}/playlists?part=snippet,status',
			headers=self.HEADERS,
			json={
				'snippet': {
					'title': playlist.title,
					'description': playlist.description,
				},
				'status': {'privacyStatus': PRIVACY_STATUS},
			},
		)
		# Invalid JSON error
		try:
			data = response.json()
		except Exception as e:
			print(f'Error parsing Youtube create playlist response JSON: {e}')
			return ApiError(
				status_code=response.status_code,
				message='Error parsing response JSON',
			)

		# Youtube API error
		if response.status_code != 200:
			return ApiError(
				status_code=response.status_code,
				message=data['error']['message'],
			)

		playlist.author = data['snippet']['channelTitle']
		playlist.id = data['id']
		playlist.songs = []

		# Happy case
		return ApiSuccess(
			status_code=response.status_code,
			data=playlist,
			message='Successfully created playlist',
		)

	def _build_search_query(self, query: ApiSearchQuery) -> str:
		return f'"{query.artist_name}" "{query.song_title}"'

	def search_song(
		self, query: ApiSearchQuery
	) -> ApiSuccess[list[ApiSong]] | ApiError:
		request_url = f'{self.API_BASE_URL}/search'

		response = requests.get(
			request_url,
			headers=self.HEADERS,
			params={
				'q': self._build_search_query(query),
				'type': 'video',
				'part': 'snippet',
				'maxResults': 5,
				'regionCode': 'CH',
			},
		)

		try:
			data = response.json()
			print(f'Search response data: {data}')
		except Exception as e:
			print(f'Error parsing Youtube search query response JSON: {e}')
			return ApiError(
				status_code=response.status_code,
				message='Failed to parse JSON',
			)

		# Youtube API error
		if response.status_code != 200:
			return ApiError(
				status_code=response.status_code,
				message='Youtube API Error',
			)

		result: list[ApiSong] = []

		try:
			tracks = data['items']
			for track in tracks:
				result.append(
					ApiSong(
						song_id=track['id']['videoId'],
						title=track['snippet']['title'],
						artist=track['snippet']['channelTitle'],
						image_url=track['snippet']['thumbnails']['default']['url']
						if track['snippet']['thumbnails']
						and track['snippet']['thumbnails']['default']
						else None,
						release_date=track['snippet']['publishedAt'],
						duration_ms=-1,
					)
				)
			print(f'Parsed search results: {len(result)} songs')
		except Exception as e:
			return ApiError(
				status_code=500,
				message=f'Error parsing song list. Exception: {e}',
			)
		return ApiSuccess(
			status_code=200, data=result, message='Successfully retrieved songs'
		)
