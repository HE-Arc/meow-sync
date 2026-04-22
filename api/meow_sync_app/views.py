import logging
import random
import string
from datetime import datetime, timedelta

import rest_framework.viewsets
from django.contrib.auth.models import User
from drf_spectacular.utils import (
	OpenApiParameter,
	OpenApiResponse,
	extend_schema,
	extend_schema_view,
)
from rest_framework import serializers, status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
	Comment,
	MusicProvider,
	OAuthConnection,
	OAuthState,
	PlaylistSynchronization,
	SongIdTranslation,
)
from .music_providers_api.ApiInterface import (
	ApiError,
	ApiInterface,
	ApiSearchQuery,
	ApiSong,
	ApiSuccess,
	ApiUser,
)
from .music_providers_api.SpotifyApi import SpotifyApi
from .music_providers_api.YoutubeApi import YoutubeApi
from .permissions import IsAuthorOrReadOnly
from .serializers import (
	CommentSerializer,
	MeSerializer,
	OAuthCallbackSuccessSerializer,
	OAuthLoginResponseSerializer,
	OAuthMessageSerializer,
	PlaylistSynchronizationSerializer,
	ProviderPlaylistsResponseSerializer,
	ProviderSinglePlaylistsResponseSerializer,
	SearchResponseSerializer,
	SongIdTranslationSerializer,
	SyncPlaylistResponseSerializer,
)

logger = logging.getLogger(__name__)


PROVIDER_PARAMETER = OpenApiParameter(
	name='provider',
	type=str,
	location=OpenApiParameter.PATH,
	required=True,
	enum=[m.value for m in MusicProvider],
	description='Music provider identifier.',
)

PLAYLIST_SYNC_ID_PARAMETER = OpenApiParameter(
	name='playlist_sync_id',
	type=int,
	location=OpenApiParameter.PATH,
	required=True,
	description='Playlist sync id.',
)

CODE_PARAMETER = OpenApiParameter(
	name='code',
	type=str,
	location=OpenApiParameter.QUERY,
	required=True,
	description='OAuth authorization code returned by the provider.',
)

STATE_PARAMETER = OpenApiParameter(
	name='state',
	type=str,
	location=OpenApiParameter.QUERY,
	required=True,
	description='Opaque OAuth state value created by the login endpoint.',
)

ARTIST_PARAMETER = OpenApiParameter(
	name='artistName',
	type=str,
	location=OpenApiParameter.QUERY,
	required=True,
	description='Search artist name for YouTube videos.',
)

MUSICNAME_PARAMETER = OpenApiParameter(
	name='musicName',
	type=str,
	location=OpenApiParameter.QUERY,
	required=True,
	description='Search music name for YouTube videos.',
)
INVERSE_PARAMETER = OpenApiParameter(
	name='inverse',
	type=bool,
	location=OpenApiParameter.QUERY,
	required=False,
	description='Inverse sync order (from second provider to first)',
)


def _ensure_access_token_valid(oauth_connection: OAuthConnection) -> bool:
	if oauth_connection.token_expires_at.timestamp() > datetime.now().timestamp():
		return True

	provider_api_class = get_api_interface_class_for_provider(oauth_connection.provider)
	if not provider_api_class:
		logger.warning(
			f'Could not find API class for provider {oauth_connection.provider} when refreshing tokens.'
		)
		return False

	try:
		new_tokens = provider_api_class.refresh_token(oauth_connection.refresh_token)

		oauth_connection.access_token = new_tokens.access_token
		oauth_connection.refresh_token = new_tokens.refresh_token
		oauth_connection.token_expires_at = datetime.now() + timedelta(
			seconds=(new_tokens.expires_in - 5)
		)
		oauth_connection.save()
		return True
	except Exception as e:
		logger.error(
			f'Error refreshing tokens for provider {oauth_connection.provider}: {e}'
		)
		return False


def _get_oauth_connection_for_user_and_provider(
	user: User, provider: str
) -> OAuthConnection | None:
	try:
		connection = OAuthConnection.objects.filter(user=user, provider=provider).last()
		if not connection:
			raise OAuthConnection.DoesNotExist
		if _ensure_access_token_valid(connection):
			return connection
		else:
			logger.warning(
				f'Access token for provider {provider} is expired and could not be refreshed.'
			)
			return None
	except OAuthConnection.DoesNotExist:
		logger.error(
			f'No OAuthConnection found for user {user.username} and provider {provider}.'
		)
		return None


def random_str_alphanum(length: int) -> str:
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_api_interface_class_for_provider(provider: str) -> type[ApiInterface] | None:
	PROVIDER_CLASS_MAP = {
		'spotify': SpotifyApi,
		'youtube': YoutubeApi,
	}

	try:
		return PROVIDER_CLASS_MAP[provider]
	except Exception as e:
		logger.error(f'Error getting API interface class for provider {provider}: {e}')
		return None


@extend_schema_view(
	get=extend_schema(
		tags=['oauth'],
		summary='Start OAuth login flow',
		description='Creates an OAuth state token and returns the provider login URL.',
		parameters=[PROVIDER_PARAMETER],
		responses={
			200: OAuthLoginResponseSerializer,
			400: OpenApiResponse(description='Invalid provider.'),
		},
	)
)
class OAuthLoginView(APIView):
	authentication_classes = [TokenAuthentication, BasicAuthentication]

	def get(self, request, provider: str) -> Response:
		if provider not in MusicProvider.values:
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MusicProvider.values)}'
			)

		oauth_state = OAuthState(
			user=request.user if request.user.is_authenticated else None,
			provider=provider,
			state=random_str_alphanum(250),
		)
		oauth_state.save()

		provider_api_class = get_api_interface_class_for_provider(oauth_state.provider)

		if not provider_api_class:
			return Response(
				{'message': f'Provider {provider} is not supported.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		return Response(
			{
				'provider': provider,
				'state': oauth_state.state,
				'login_url': provider_api_class.login_url(oauth_state.state),
			},
			status=status.HTTP_200_OK,
		)


@extend_schema_view(
	get=extend_schema(
		tags=['oauth'],
		summary='Handle OAuth callback',
		description='Exchanges the provider code for tokens and returns the API auth token.',
		parameters=[PROVIDER_PARAMETER, CODE_PARAMETER, STATE_PARAMETER],
		responses={
			201: OAuthCallbackSuccessSerializer,
			404: OAuthMessageSerializer,
			500: OAuthMessageSerializer,
		},
	)
)
class OAuthCallbackView(APIView):
	def get(self, request, provider: str) -> Response:
		code = request.GET.get('code')
		state = request.GET.get('state')
		logger.debug(
			f'OAuth  callback with state: {state}, code: {code}, provider: {provider}'
		)

		try:
			oauth_state = OAuthState.objects.get(state=state)

			provider_api_class = get_api_interface_class_for_provider(
				oauth_state.provider
			)
			if not provider_api_class:
				return Response(
					{'message': f'Provider {provider} is not supported.'},
					status=status.HTTP_400_BAD_REQUEST,
				)

			provider_tokens = provider_api_class.get_tokens(code=code)

			provider_api_instance = provider_api_class(
				access_token=provider_tokens.access_token
			)
			provider_user_response: ApiSuccess[ApiUser] | ApiError = (
				provider_api_instance.get_current_user()
			)

			if not provider_user_response.success:
				logger.info(
					f'Could not get user data for provider {oauth_state.provider} - {provider_user_response.message}'
				)
				return Response(
					{
						'message': f'Could not get user data for provider {oauth_state.provider} - {provider_user_response.message}'
					},
					status=provider_user_response.status_code,
				)
			try:
				if not provider_user_response.data:
					logger.error(
						f'Provider {oauth_state.provider} returned success but no user data.'
					)
					return Response(
						{
							'message': f'Provider {oauth_state.provider} returned success but no user data.'
						},
						status=status.HTTP_500_INTERNAL_SERVER_ERROR,
					)
				# existing connection
				oauth_connection = OAuthConnection.objects.filter(
					provider=provider, provider_user_id=provider_user_response.data.id
				).first()

				if oauth_connection is None:
					raise OAuthConnection.DoesNotExist

				current_user = request.user if request.user.is_authenticated else None
				# sync users when connecting with a second social provider
				if (
					current_user
					and current_user.username != oauth_connection.user.username
				):
					oauth_connection.user = current_user

				oauth_connection.access_token = provider_tokens.access_token
				oauth_connection.refresh_token = provider_tokens.refresh_token
				oauth_connection.token_expires_at = datetime.now() + timedelta(
					seconds=(provider_tokens.expires_in - 5)
				)
				oauth_connection.save()

				user = oauth_connection.user
				auth_token, created = Token.objects.get_or_create(user=user)

				return Response(
					{
						'message': f'Successfully connected with {MusicProvider(provider).label}. (existing user)',
						'auth_token': auth_token.key,
					},
					status=status.HTTP_201_CREATED,
				)

			except OAuthConnection.DoesNotExist:
				# new user
				if not oauth_state.user:
					username = f'user_{random_str_alphanum(12)}'
					# set username from name on provider platform if available
					if not provider_user_response.data:
						raise ValueError(
							'Provider user response was successful but contained no data.'
						)

					if provider_user_response.data.name:
						username = (
							provider_user_response.data.name[:240]
							.lower()
							.replace('  ', ' ')  # replace double spaces
							.replace(' ', '_')[
								# replace spaces with '_'
								:245
							]  # truncate string
							+ '_'
							+ random_str_alphanum(4)
						)  # some randomness for users with same name

					user = User.objects.create(
						username=username, password=random_str_alphanum(255)
					)
					user.save()
					oauth_state.user = user
					oauth_state.save()

				user = oauth_state.user
				if not provider_user_response.data:
					raise ValueError(
						'Provider user response was successful but contained no data.'
					)

				oauth_connection = OAuthConnection(
					user=user,
					provider=oauth_state.provider,
					provider_user_id=provider_user_response.data.id,
					access_token=provider_tokens.access_token,
					refresh_token=provider_tokens.refresh_token,
					token_expires_at=datetime.now()
					+ timedelta(seconds=(provider_tokens.expires_in - 5)),
				)
				oauth_connection.save()

				auth_token, created = Token.objects.get_or_create(user=user)

				return Response(
					{
						'message': f'Successfully connected with {MusicProvider(provider).label}. (new user)',
						'auth_token': auth_token.key,
					},
					status=status.HTTP_201_CREATED,
				)

		except OAuthState.DoesNotExist:
			logger.error(f'OAuthState does not exist for state: {state}')
			return Response(
				{'message': 'Invalid state'},
				status=status.HTTP_404_NOT_FOUND,
			)
		except OAuthState.MultipleObjectsReturned:
			logger.critical(
				f'More than one OAuthState with the same state: {state}. Something went horribly wrong.'
			)

			return Response(
				{
					'message': f'More than one OAuthState with the same state: {state}. Something went horribly wrong.'
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)


@extend_schema_view(
	delete=extend_schema(
		tags=['oauth'],
		summary='Disconnect OAuth provider',
		description='Deletes the authenticated user connection for the selected provider.',
		parameters=[PROVIDER_PARAMETER],
		responses={
			200: OAuthMessageSerializer,
			404: OAuthMessageSerializer,
			500: OAuthMessageSerializer,
		},
	)
)
class OAuthDisconnectView(APIView):
	permission_classes = [IsAuthenticated]

	def delete(self, request, provider: str):
		if provider not in MusicProvider.values:
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MusicProvider.values)}'
			)

		current_user = request.user
		try:
			connection = OAuthConnection.objects.filter(
				user=current_user, provider=provider
			)
			if len(connection) == 0:
				raise OAuthConnection.DoesNotExist
			for c in connection:
				c.delete()
			return Response(
				{
					'message': f'Successfully disconnected from {MusicProvider(provider).label}.'
				},
				status=status.HTTP_200_OK,
			)
		except OAuthConnection.DoesNotExist:
			logger.error(f'OAuthConnection does not exist for provider: {provider}')
			return Response(
				{'message': f'OAuthConnection does not exist for provider: {provider}'},
				status=status.HTTP_404_NOT_FOUND,
			)


@extend_schema(
	tags=['users'],
	summary='Get current user',
	responses={200: MeSerializer},
)
class MeView(APIView):
	authentication_classes = [TokenAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request) -> Response:
		return Response(MeSerializer(request.user).data)


@extend_schema(
	tags=['provider'],
	summary='Search provider for Song',
	description='Search for songs on provider. Returns a list of songs matching the query.',
	parameters=[PROVIDER_PARAMETER, ARTIST_PARAMETER, MUSICNAME_PARAMETER],
	responses={
		200: SearchResponseSerializer,
		400: OAuthMessageSerializer,
		401: OAuthMessageSerializer,
	},
)
class SearchView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, provider: str) -> Response:
		"""Search provider for songs"""
		if provider not in MusicProvider.values:
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MusicProvider.values)}'
			)

		artist_name = request.GET.get('artistName')
		song_title = request.GET.get('musicName')

		if not artist_name or not song_title:
			return Response(
				{
					'message': 'Search query parameters "artistName" and "musicName" are required'
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if not provider:
			return Response(
				{'message': 'Search query parameter "provider" is required'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		current_user = request.user
		try:
			connection = _get_oauth_connection_for_user_and_provider(
				current_user, provider
			)
		except OAuthConnection.DoesNotExist:
			return Response(
				{
					'message': f'No connection found for provider {provider}. Please connect your {provider} account first.'
				},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		provider_class = get_api_interface_class_for_provider(provider)
		provider_class_instance = provider_class(access_token=connection.access_token)

		search_result = provider_class_instance.search_song(
			ApiSearchQuery(artist_name=artist_name, song_title=song_title)
		)

		serializer = SearchResponseSerializer(
			{
				'data': search_result.data,
				'message': search_result.message,
			}
		)
		return Response(serializer.data, status=search_result.status_code)


@extend_schema(
	tags=['provider'],
	summary='Provider playlists',
	description='Interact with provider playlists',
	parameters=[PROVIDER_PARAMETER],
	responses={
		200: ProviderPlaylistsResponseSerializer,
		400: OAuthMessageSerializer,
		401: OAuthMessageSerializer,
	},
)
class ProviderPlaylistView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, provider: str):
		if provider not in MusicProvider.values:
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MusicProvider.values)}'
			)

		current_user = request.user
		try:
			connection = _get_oauth_connection_for_user_and_provider(
				current_user, provider
			)
		except OAuthConnection.DoesNotExist:
			return Response(
				{
					'message': f'No connection found for provider {provider}. Please connect your {provider} account first.'
				},
				status=status.HTTP_401_UNAUTHORIZED,
			)
		provider_class = get_api_interface_class_for_provider(provider)
		provider_class_instance = provider_class(access_token=connection.access_token)

		playlists_response = provider_class_instance.get_all_playlists()
		if not playlists_response.success:
			return Response(
				{
					'message': f'Failed to fetch playlists for provider {provider}. {playlists_response.message}'
				},
				status=playlists_response.status_code,
			)

		serializer = ProviderPlaylistsResponseSerializer(
			{
				'data': playlists_response.data,
				'message': playlists_response.message,
			}
		)

		return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
	tags=['provider'],
	summary='Get single playlist',
	description='Interact with provider playlists',
	parameters=[PROVIDER_PARAMETER],
	responses={
		200: ProviderSinglePlaylistsResponseSerializer,
		400: OAuthMessageSerializer,
		401: OAuthMessageSerializer,
	},
)
class ProviderSinglePlaylistView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, provider: str, playlist_id: str):
		if provider not in MusicProvider.values:
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MusicProvider.values)}'
			)

		current_user = request.user
		try:
			connection = _get_oauth_connection_for_user_and_provider(
				current_user, provider
			)
		except OAuthConnection.DoesNotExist:
			return Response(
				{
					'message': f'No connection found for provider {provider}. Please connect your {provider} account first.'
				},
				status=status.HTTP_401_UNAUTHORIZED,
			)
		provider_class = get_api_interface_class_for_provider(provider)
		provider_class_instance = provider_class(access_token=connection.access_token)

		playlist_response = provider_class_instance.get_playlist(playlist_id)
		if not playlist_response.success:
			return Response(
				{
					'message': f'Failed to fetch playlist for provider {provider}. {playlist_response.message}'
				},
				status=playlist_response.status_code,
			)

		serializer = ProviderSinglePlaylistsResponseSerializer(
			{
				'data': playlist_response.data,
				'message': playlist_response.message,
			}
		)

		return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
	tags=['provider'],
	summary='Sync playlists',
	description='Interact with provider playlists',
	parameters=[PLAYLIST_SYNC_ID_PARAMETER, INVERSE_PARAMETER],
	responses={
		200: SyncPlaylistResponseSerializer,
		400: OAuthMessageSerializer,
		401: OAuthMessageSerializer,
	},
)
class SyncPlaylist(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, playlist_sync_id: int):
		current_user = request.user

		inverse = True if request.GET.get('inverse') == 'true' else False
		logger.debug('INVERSE: ', inverse)

		try:
			playlist_sync: PlaylistSynchronization = (
				PlaylistSynchronization.objects.get(
					id=playlist_sync_id, user=current_user
				)
			)
		except PlaylistSynchronization.DoesNotExist:
			return Response(
				{
					'message': f'No playlist synchronization found with id {playlist_sync_id} for current user.'
				},
				status=status.HTTP_404_NOT_FOUND,
			)

		if inverse:
			playlist_sync.pk = None  # prevent saving
			playlist_sync.first_provider, playlist_sync.second_provider = (
				playlist_sync.second_provider,
				playlist_sync.first_provider,
			)
			playlist_sync.first_playlist_id, playlist_sync.second_playlist_id = (
				playlist_sync.second_playlist_id,
				playlist_sync.first_playlist_id,
			)

		try:
			connection_1 = _get_oauth_connection_for_user_and_provider(
				current_user, playlist_sync.first_provider
			)
			connection_2 = _get_oauth_connection_for_user_and_provider(
				current_user, playlist_sync.second_provider
			)
		except OAuthConnection.DoesNotExist:
			return Response(
				{'message': 'No connection found for one of the providers.'},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		provider_class_1 = get_api_interface_class_for_provider(
			playlist_sync.first_provider
		)
		provider_class_2 = get_api_interface_class_for_provider(
			playlist_sync.second_provider
		)
		provider_class_instance_1: ApiInterface = provider_class_1(
			access_token=connection_1.access_token
		)
		provider_class_instance_2: ApiInterface = provider_class_2(
			access_token=connection_2.access_token
		)

		# get songs for first provider
		playlist_response_1 = provider_class_instance_1.get_playlist(
			playlist_sync.first_playlist_id, include_songs=True
		)
		if not playlist_response_1.success:
			return Response(
				{
					'message': f'Failed to fetch songs for provider {playlist_sync.first_provider} and playlist {playlist_sync.first_playlist_id}. {playlist_response_1.message}'
				},
				status=playlist_response_1.status_code,
			)
		songs_original = playlist_response_1.data.songs

		# get songs for second provider
		playlist_response_2 = provider_class_instance_2.get_playlist(
			playlist_sync.second_playlist_id, include_songs=True
		)
		if not playlist_response_2.success:
			return Response(
				{
					'message': f'Failed to fetch songs for provider {playlist_sync.second_provider} and playlist {playlist_sync.second_playlist_id}. {playlist_response_2.message}'
				},
				status=playlist_response_2.status_code,
			)

		songs_target_ids = [s.id for s in playlist_response_2.data.songs]

		# translate songs
		songs_translated = []
		error_bag = []
		for song_o in songs_original:
			# check cache
			cached_translation = None
			if playlist_sync.first_provider == 'spotify':
				cached_translation = SongIdTranslation.objects.filter(
					spotify_id=song_o.id
				).first()
				logger.debug('CACHED LOOKUP SPOTIFY ', cached_translation)
			elif playlist_sync.first_provider == 'youtube':
				logger.debug('CACHED LOOKUP YOUTUBE ', cached_translation)
				cached_translation = SongIdTranslation.objects.filter(
					youtube_id=song_o.id
				).first()
			else:
				raise Exception('provider not implemented')

			if cached_translation:
				logger.debug('CACHED FOUND !!')
				# do not add same song twice
				if (
					cached_translation.spotify_id in songs_target_ids
					or cached_translation.youtube_id in songs_target_ids
				):
					continue

				if playlist_sync.second_provider == 'spotify':
					songs_translated.append(
						ApiSong(
							song_id=cached_translation.spotify_id,
							artist='unset, fetched from translation cache',
							duration_ms=-1,
							id_in_playlist=-1,
							image_url='unset, fetched from translation cache',
							release_date='unset, fetched from translation cache',
							title='unset, fetched from translation cache',
						)
					)
				elif playlist_sync.second_provider == 'youtube':
					songs_translated.append(
						ApiSong(
							song_id=cached_translation.youtube_id,
							artist='unset, fetched from translation cache',
							duration_ms=-1,
							id_in_playlist=-1,
							image_url='unset, fetched from translation cache',
							release_date='unset, fetched from translation cache',
							title='unset, fetched from translation cache',
						)
					)
				else:
					raise Exception('provider not implemented')

				continue
			else:
				logger.debug('no cache found, searching via API')
				# search on provider and update cache
				search_response = provider_class_instance_2.search_song(
					ApiSearchQuery(artist_name=song_o.artist, song_title=song_o.title)
				)
				if not search_response.success:
					error_bag.append(
						f'[provider: {playlist_sync.second_provider}, title: {song_o.title}, artist: {song_o.artist}] {search_response.message}'
					)
					continue

				search_results = search_response.data
				if len(search_results) == 0:
					error_bag.append(
						f'[provider: {playlist_sync.second_provider}, title: {song_o.title}, artist: {song_o.artist}] No corresponding song found.'
					)
					continue
				search_result = search_results[0]

				# do not add same song twice
				if search_result.id in songs_target_ids:
					continue

				# add song to translation cache
				cached_translation = SongIdTranslation(
					spotify_id=song_o.id
					if playlist_sync.first_provider == 'spotify'
					else search_result.id,
					youtube_id=song_o.id
					if playlist_sync.first_provider == 'youtube'
					else search_result.id,
				)
				logger.debug('caching transition: ', cached_translation)
				cached_translation.save()

				songs_translated.append(search_result)

		translated_ids = [s.id for s in songs_translated]

		add_song_response = provider_class_instance_2.add_to_playlist(
			playlist_sync.second_playlist_id, translated_ids
		)

		message = 'Successfully synced playlists.'
		current_status = status.HTTP_200_OK

		if len(error_bag) > 0:
			message = ('Failed to sync some songs.',)
			current_status = (status.HTTP_206_PARTIAL_CONTENT,)

		if not add_song_response.success:
			message = f'Unable to add songs to playlist for {playlist_sync.second_provider}. {add_song_response.message}'
			current_status = add_song_response.status_code

		serializer = SyncPlaylistResponseSerializer(
			{'message': message, 'errors': error_bag}
		)

		return Response(serializer.data, status=current_status)


class CommentViewSet(rest_framework.viewsets.ModelViewSet):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
	authentication_classes = [TokenAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class PlaylistSynchronizationViewSet(rest_framework.viewsets.ModelViewSet):
	queryset = PlaylistSynchronization.objects.all()
	serializer_class = PlaylistSynchronizationSerializer
	authentication_classes = [TokenAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class SongIdTranslationViewSet(rest_framework.viewsets.ModelViewSet):
	queryset = SongIdTranslation.objects.all()
	serializer_class = SongIdTranslationSerializer
	authentication_classes = [TokenAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
