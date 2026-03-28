import random
import string
import rest_framework.viewsets
from datetime import datetime, timedelta
from .models import Comment, OAuthState, OAuthConnection, MUSIC_PROVIDERS
from .serializers import (
	CommentSerializer,
	OAuthCallbackSuccessSerializer,
	OAuthLoginResponseSerializer,
	OAuthMessageSerializer,
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
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .music_providers_api.ApiInterface import *
from .music_providers_api.SpotifyApi import *
from .music_providers_api.YoutubeApi import *
from django.contrib.auth.models import User


PROVIDER_PARAMETER = OpenApiParameter(
	name='provider',
	type=str,
	location=OpenApiParameter.PATH,
	required=True,
	enum=list(MUSIC_PROVIDERS.keys()),
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


def random_str_alphanum(length: int) -> str:
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_api_interface_class_for_provider(provider: str) -> ApiInterface | None:
	PROVIDER_CLASS_MAP = {
		'spotify': SpotifyApi,
		'youtube': YoutubeApi,
	}

	try:
		return PROVIDER_CLASS_MAP[provider]
	except:
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
	def get(self, request, provider: str) -> Response:
		if provider not in MUSIC_PROVIDERS.keys():
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MUSIC_PROVIDERS.keys())}'
			)

		oauth_state = OAuthState(
			user=request.user if request.user.is_authenticated else None,
			provider=provider,
			state=random_str_alphanum(250),
		)
		oauth_state.save()

		provider_api_class = get_api_interface_class_for_provider(oauth_state.provider)

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
			provider_tokens: ApiTokens = provider_api_class.get_tokens(code=code)

			provider_api_instance = provider_api_class(
				access_token=provider_tokens.access_token
			)
			provider_user_response: ApiResponse[ApiUser] = (
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
				# existing connection
				oauth_connection = OAuthConnection.objects.get(
					provider=provider, provider_user_id=provider_user_response.data.id
				)

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
						'message': f'Successfully connected with {MUSIC_PROVIDERS[provider]}. (existing user)',
						'auth_token': auth_token.key,
					},
					status=status.HTTP_201_CREATED,
				)

			except OAuthConnection.DoesNotExist:
				# new user
				if not oauth_state.user:
					username = f'user_{random_str_alphanum(12)}'
					# set username from name on provider platform if available
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
						'message': f'Successfully connected with {MUSIC_PROVIDERS[provider]}. (new user)',
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
		if provider not in MUSIC_PROVIDERS.keys():
			raise serializers.ValidationError(
				f'This field must be an valid provider. providers: {" ".join(MUSIC_PROVIDERS.keys())}'
			)

		current_user = request.user
		try:
			OAuthConnection.objects.get(user=current_user, provider=provider)
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


class CommentViewSet(rest_framework.viewsets.ModelViewSet):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
