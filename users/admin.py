from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = [
        "username",
        "email",
        "discord_tag",
        "reputation",
        "is_staff",
        "date_joined"
    ]

    list_filter = [
        "is_staff",
        "is_active",
        "date_joined"
    ]

    search_fields = ["username", "email", "discord_tag"]

    fieldsets = (
        ("Authentication", {
            "fields": ("username", "password")
        }),
        ("Personal Info", {
            "fields": ("email", "bio", "avatar")
        }),
        ("Gaming Platforms", {
            "fields": ("discord_tag", "steam_url"),
        }),
        ("Extra Data", {
            "fields": ("reputation",),
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )
