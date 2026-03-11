from django.contrib import admin  # noqa: F401
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Auth Tokens", {
            "fields": ("spotify_token", "youtube_token"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Auth Tokens", {
            "fields": ("spotify_token", "youtube_token"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)