import os
import base64
import time
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


class SpotifyApi(ApiInterface):
	CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
	CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
	REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

	AUTH_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'
	API_BASE_URL = 'https://api.spotify.com/v1'
	SEARCH_QUERY_MARKET = 'CH'

	@classmethod
	def login_url(cls, state: str) -> str:
		scope = 'playlist-read-private,playlist-read-collaborative,playlist-modify-public,playlist-modify-private'

		params = {
			'response_type': 'code',
			'client_id': cls.CLIENT_ID,
			'scope': scope,
			'redirect_uri': cls.REDIRECT_URI,
			'state': state,
		}

		url = requests.Request('GET', cls.AUTH_URL, params=params).prepare().url
		if not url:
			raise Exception('Failed to construct Spotify login URL')
		return url

	@classmethod
	def get_tokens(cls, code: str) -> ApiTokens:
		auth_header = base64.b64encode(
			f'{cls.CLIENT_ID}:{cls.CLIENT_SECRET}'.encode()
		).decode()

		token_data = {
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': cls.REDIRECT_URI,
		}

		token_headers = {
			'Authorization': f'Basic {auth_header}',
			'Content-Type': 'application/x-www-form-urlencoded',
		}

		response = requests.post(cls.TOKEN_URL, data=token_data, headers=token_headers)
		token_info = response.json()

		print(token_info)

		access_token = token_info['access_token']
		refresh_token = token_info['refresh_token']
		expires_in = token_info['expires_in']

		return ApiTokens(
			access_token=access_token,
			refresh_token=refresh_token,
			expires_in=expires_in,
		)

	@classmethod
	def refresh_token(cls, refresh_token: str) -> ApiTokens:
		auth_header = base64.b64encode(
			f'{cls.CLIENT_ID}:{cls.CLIENT_SECRET}'.encode()
		).decode()

		token_data = {
			'grant_type': 'refresh_token',
			'refresh_token': refresh_token,
		}

		token_headers = {
			'Authorization': f'Basic {auth_header}',
			'Content-Type': 'application/x-www-form-urlencoded',
		}

		response = requests.post(cls.TOKEN_URL, data=token_data, headers=token_headers)
		token_info = response.json()

		access_token = token_info['access_token']
		new_refresh_token = token_info.get('refresh_token', refresh_token)
		expires_in = token_info['expires_in']

		return ApiTokens(
			access_token=access_token,
			refresh_token=new_refresh_token,
			expires_in=expires_in,
		)

	def __init__(self, access_token: str):
		self.HEADERS = {'Authorization': f'Bearer {access_token}'}
		self.MAX_SONG_CHUNK_SIZE = 100

	def get_current_user(self) -> ApiSuccess[ApiUser] | ApiError:
		CURRENT_USER_URL = f'{self.API_BASE_URL}/me'

		while True:
			current_user_response = requests.get(CURRENT_USER_URL, headers=self.HEADERS)
			if not self._handle_rate_limit(current_user_response):
				break

		try:
			data = current_user_response.json()
		except Exception as e:
			print(f'Error parsing Spotify current user response JSON: {e}')
			return ApiError(
				status_code=current_user_response.status_code,
				message='Error parsing response JSON',
			)

		# Spotify API error
		if current_user_response.status_code != 200:
			return ApiError(
				status_code=current_user_response.status_code,
				message=data.get('error', {}).get('message', 'Spotify API Error'),
			)

		return ApiSuccess(
			status_code=current_user_response.status_code,
			data=ApiUser(name=data['display_name'], user_id=data['id']),
		)

	def get_all_playlists(self) -> ApiSuccess[list[ApiPlaylist]] | ApiError:
		current_page_url = f'{self.API_BASE_URL}/me/playlists'
		result: list[ApiPlaylist] = []
		while True:
			while True:
				playlist_response = requests.get(current_page_url, headers=self.HEADERS)
				if not self._handle_rate_limit(playlist_response):
					break
			# Invalid JSON error
			try:
				data = playlist_response.json()
			except Exception as e:
				print(f'Error parsing Spotify playlists response JSON: {e}')
				return ApiError(
					status_code=playlist_response.status_code,
					message=f'Error parsing response JSON: "{playlist_response.text}"',
				)

			# Spotify API error
			if playlist_response.status_code != 200:
				return ApiError(
					status_code=playlist_response.status_code,
					message=data['error']['message'],
				)

			# Happy case
			for playlist in data['items']:
				songs: list[ApiSong] = []

				result.append(
					ApiPlaylist(
						playlist_id=playlist['id'],
						title=playlist['name'],
						description=playlist['description'],
						author=playlist['owner']['display_name'],
						image_url=playlist['images'][0]['url']
						if playlist['images'] and playlist['images'][0]
						else None,
						songs=songs,
					)
				)

			if not data['next']:
				break
			current_page_url = data['next']

		return ApiSuccess(
			status_code=playlist_response.status_code,
			data=result,
		)

	def _get_playlist_info(self, playlist_id: str) -> ApiPlaylist:
		request_url = f'{self.API_BASE_URL}/playlists/{playlist_id}'

		while True:
			playlist_response = requests.get(request_url, headers=self.HEADERS)
			if not self._handle_rate_limit(playlist_response):
				break

		data = playlist_response.json()

		# Spotify API error
		if playlist_response.status_code != 200:
			raise Exception(
				f'{data["error"]["message"]}, status_code: {playlist_response.status_code}'
			)

		# Happy case
		result = ApiPlaylist(
			playlist_id=data['id'],
			title=data['name'],
			description=data['description'],
			author=data['owner']['display_name'],
			image_url=data['images'][0]['url']
			if data['images'] and data['images'][0]
			else None,
			songs=[],
		)

		return result

	def get_playlist(
		self, playlist_id: str, include_songs=False
	) -> ApiSuccess[ApiPlaylist] | ApiError:
		current_song_page_url = f'{self.API_BASE_URL}/playlists/{playlist_id}/items'

		try:
			result = self._get_playlist_info(playlist_id)
		except Exception as ex:
			return ApiError(status_code=500, message=str(ex))

		songs = []
		# get playlist songs

		while True and include_songs:
			while True:
				playlist_songs_response = requests.get(
					current_song_page_url, headers=self.HEADERS
				)
				if not self._handle_rate_limit(playlist_songs_response):
					break
			# Invalid JSON error
			try:
				data = playlist_songs_response.json()
			except Exception as e:
				print(f'Error parsing Spotify playlist songs response JSON: {e}')
				return ApiError(
					status_code=playlist_songs_response.status_code,
					message='Error parsing response JSON',
				)

			# Spotify API error
			if playlist_songs_response.status_code != 200:
				return ApiError(
					status_code=playlist_songs_response.status_code,
					message=data['error']['message']
					if data.get('error')
					else 'Spotify Api Error',
				)

			# Happy case
			for song in data['items']:
				song_data = song['track']
				songs.append(
					ApiSong(
						song_id=song_data['id'],
						title=song_data['name'],
						artist=', '.join(
							artist['name'] for artist in song_data['artists']
						),
						image_url=song_data['album']['images'][0]['url']
						if song_data['album']['images']
						and song_data['album']['images'][0]
						else None,
						release_date=song_data['album']['release_date'],
						duration_ms=song_data['duration_ms'],
					)
				)
			if not data['next']:
				break
			current_song_page_url = data['next']

		result.songs = songs

		return ApiSuccess(status_code=200, data=result)

	def _song_id_to_uri(self, song_ids: list[str]):
		prefix = 'spotify:track:'
		result = list(map(lambda song: prefix + song, song_ids))

		return result

	def _chunk_list(self, lst: list, chunk_size: int):
		return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

	def add_to_playlist(
		self, playlist_id: str, song_ids: list[str]
	) -> ApiSuccess[None] | ApiError:
		chunked_ids = self._chunk_list(song_ids, self.MAX_SONG_CHUNK_SIZE)

		for chunk in chunked_ids:
			request_url = f'{self.API_BASE_URL}/playlists/{playlist_id}/items'

			request_body = {'uris': self._song_id_to_uri(chunk)}

			while True:
				response = requests.post(
					request_url, json=request_body, headers=self.HEADERS
				)
				if not self._handle_rate_limit(response):
					break

			try:
				data = response.json()
				# Spotify API error
				if response.status_code != 201:
					return ApiError(
						status_code=response.status_code,
						message=data['error']['message'],
					)
			except Exception as e:
				print(f'Error parsing Spotify add to playlist response JSON: {e}')
				return ApiError(
					status_code=response.status_code,
					message='Error parsing response JSON',
				)

		return ApiSuccess(
			status_code=201,
			data=None,
			message='Successfully added songs to playlist',
		)

	def remove_from_playlist(
		self, playlist_id: str, song_ids: list[str]
	) -> ApiSuccess[None] | ApiError:
		chunked_ids = self._chunk_list(song_ids, self.MAX_SONG_CHUNK_SIZE)

		for chunk in chunked_ids:
			request_url = f'{self.API_BASE_URL}/playlists/{playlist_id}/items'

			request_body = {
				'items': [{'uri': uri} for uri in self._song_id_to_uri(chunk)]
			}

			while True:
				response = requests.delete(
					request_url, json=request_body, headers=self.HEADERS
				)
				if not self._handle_rate_limit(response):
					break

			try:
				data = response.json()
			except Exception as e:
				print(f'Error parsing Spotify remove from playlist response JSON: {e}')
				return ApiError(
					status_code=response.status_code,
					message='Error parsing response JSON',
				)

			# Spotify API error
			if response.status_code != 200:
				return ApiError(
					status_code=response.status_code,
					message=data['error']['message'],
				)

		# Happy case
		return ApiSuccess(
			status_code=200,
			data=None,
			message='Successfully removed songs from playlist',
		)

	def create_playlist(
		self, playlist: ApiPlaylist
	) -> ApiSuccess[ApiPlaylist] | ApiError:
		request_url = f'{self.API_BASE_URL}/me/playlists'
		PLAYLIST_PUBLIC = False
		PLAYLIST_COLLABORATIVE = False

		request_body = {
			'name': playlist.title,
			'description': playlist.description,
			'collaborative': PLAYLIST_COLLABORATIVE,
			'public': PLAYLIST_PUBLIC,
		}

		while True:
			response = requests.post(
				request_url, json=request_body, headers=self.HEADERS
			)
			if not self._handle_rate_limit(response):
				break

		# Json error
		try:
			data = response.json()
		except Exception as e:
			print(f'Error parsing Spotify create playlist response JSON: {e}')
			return ApiError(
				status_code=response.status_code,
				message='Failed to parse JSON',
			)

		# Spotify API error
		if response.status_code != 201:
			return ApiError(
				status_code=response.status_code,
				message='Spotify API Error',
			)

		playlist.author = data['owner']['display_name']
		playlist.id = data['id']
		playlist.songs = []

		# Happy case
		return ApiSuccess(
			status_code=response.status_code,
			data=playlist,
			message='Successfully created playlist',
		)

	def _song_query_string(self, artist_name: str, song_title: str) -> str:
		return f'track:{song_title} artist:{artist_name}'

	def search_song(
		self, query: ApiSearchQuery, retry=True, exact=True
	) -> ApiSuccess[list[ApiSong]] | ApiError:
		request_url = f'{self.API_BASE_URL}/search'
		request_params = {
			'q': self._song_query_string(
				artist_name=query.artist_name,
				song_title=query.song_title,
			)
			if exact
			else f'{query.artist_name} {query.song_title}'.strip(),
			'type': 'track',
			'market': self.SEARCH_QUERY_MARKET,
			'offset': 0,
			'limit': 10,
		}

		while True:
			response = requests.get(
				request_url, params=request_params, headers=self.HEADERS
			)
			if not self._handle_rate_limit(response):
				break

		try:
			data = response.json()
		except Exception as e:
			print(f'Error parsing Spotify search query response JSON: {e}')
			return ApiError(
				status_code=response.status_code,
				message='Failed to parse JSON',
			)

		# Spotify API error
		if response.status_code != 200:
			return ApiError(
				status_code=response.status_code,
				message='Spotify API Error',
			)

		result: list[ApiSong] = []

		try:
			tracks = data['tracks']['items']
			for track in tracks:
				result.append(
					ApiSong(
						song_id=track['id'],
						artist=', '.join(artist['name'] for artist in track['artists']),
						title=track['name'],
						duration_ms=track['duration_ms'],
						image_url=track['album']['images'][0]['url']
						if track['album']['images'] and track['album']['images'][0]
						else None,
						release_date=track['album']['release_date'],
					)
				)
		except Exception as e:
			raise e
			return ApiError(
				status_code=500,
				message=f'Error parsing song list. Exception: {e}',
			)

		if len(result) == 0 and retry:
			if exact:
				return self.search_song(query=query, retry=True, exact=False)
			if not exact:
				return self.search_song(
					query=ApiSearchQuery(artist_name='', song_title=query.song_title),
					retry=False,
					exact=False,
				)

		return ApiSuccess(
			status_code=200, data=result, message='Successfully retrieved songs'
		)

	def _handle_rate_limit(self, response: requests.Response) -> bool:
		if response.status_code == 429:
			retry_after = int(response.headers.get('Retry-After', '1'))
			print(
				f'Rate limited by Spotify API. Retrying after {retry_after} seconds...'
			)
			time.sleep(retry_after)
			return True
		return False
