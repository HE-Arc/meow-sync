"""
URL configuration for meow_sync project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from meow_sync_app.views import (
	OAuthCallbackView,
	OAuthDisconnectView,
	OAuthLoginView,
	CommentViewSet,
	MeView,
	PlaylistSynchronizationViewSet,
	SearchView,
	SongIdTranslationViewSet,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'playlists', PlaylistSynchronizationViewSet, basename='playlist')
router.register(r'songs', SongIdTranslationViewSet, basename='song')

urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
	path(
		'api/swagger/',
		SpectacularSwaggerView.as_view(url_name='schema'),
		name='swagger-ui',
	),
	# TODO: move to main app
	path(
		'api/oauth/<str:provider>/login/', OAuthLoginView.as_view(), name='oauth-login'
	),
	path(
		'api/oauth/<str:provider>/callback/',
		OAuthCallbackView.as_view(),
		name='oauth-callback',
	),
	path(
		'api/oauth/<str:provider>/disconnect/',
		OAuthDisconnectView.as_view(),
		name='oauth-disconnect',
	),
	path('api/users/me/', MeView.as_view(), name='users-me'),
	path('api/<str:provider>/search/', SearchView.as_view(), name='provider-search'),
	path('api/', include(router.urls)),
]
