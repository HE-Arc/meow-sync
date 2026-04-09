import random
import string
import rest_framework.viewsets
from datetime import datetime, timedelta

from .permissions import IsAuthorOrReadOnly
from .models import (
	Comment,
	OAuthState,
	OAuthConnection,
	MusicProvider,
	PlaylistSynchronization,
	SongIdTranslation,
)
from .serializers import (
	CommentSerializer,
	PlaylistSynchronizationSerializer,
	SongIdTranslationSerializer,
	MeSerializer,
	OAuthCallbackSuccessSerializer,
	OAuthLoginResponseSerializer,
	OAuthMessageSerializer,
	SearchResponseSerializer,
)
from drf_spectacular.utils import (
	OpenApiParameter,
	OpenApiResponse,
	extend_schema,
	extend_schema_view,
)
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .music_providers_api.ApiInterface import (
	ApiInterface,
	ApiSuccess,
	ApiError,
	ApiUser,
	ApiSearchQuery,
)
from .music_providers_api.SpotifyApi import SpotifyApi
from .music_providers_api.YoutubeApi import YoutubeApi
from django.contrib.auth.models import User


PROVIDER_PARAMETER = OpenApiParameter(
	name='provider',
	type=str,
	location=OpenApiParameter.PATH,
	required=True,
	enum=[m.value for m in MusicProvider],
	description='Music provider identifier.',
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
		print(f'Error getting API interface class for provider {provider}: {e}')
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
		print(
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
				print(
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
					print(
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
			print(f'OAuthState does not exist for state: {state}')
			return Response(
				{'message': 'Invalid state'},
				status=status.HTTP_404_NOT_FOUND,
			)
		except OAuthState.MultipleObjectsReturned:
			print(
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
			connection = OAuthConnection.objects.get(
				user=current_user, provider=provider
			)
			connection.delete()
			return Response(
				{
					'message': f'Successfully disconnected from {MusicProvider(provider).label}.'
				},
				status=status.HTTP_200_OK,
			)
		except OAuthConnection.DoesNotExist:
			print(f'OAuthConnection does not exist for provider: {provider}')
			return Response(
				{'message': f'OAuthConnection does not exist for provider: {provider}'},
				status=status.HTTP_404_NOT_FOUND,
			)
		except OAuthConnection.MultipleObjectsReturned:
			print(
				f'More than one OAuthConnection with the same provider: {provider}. Something went horribly wrong.'
			)

			return Response(
				{
					'message': f'More than one OAuthConnection with the same provider: {provider}. Something went horribly wrong.'
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
	tags=['search'],
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
			connection = OAuthConnection.objects.get(
				user=current_user, provider=provider
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
