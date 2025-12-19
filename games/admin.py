from django.contrib import admin

from games.models import (
    GameRole,
    Game,
    UserGameProfile
)


class GameRoleInLine(admin.TabularInline):
    model = GameRole
    extra = 1
    fields = ["order", "name", "icon_class"]
    ordering = ["order"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "team_size", "created_at"]
    list_filter = ["title", "team_size"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ["title"]}

    inlines = [GameRoleInLine]

    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "icon")
        }),
        ("Settings", {
            "fields": ("team_size",)
        }),
    )


@admin.register(GameRole)
class UserGameRole(admin.ModelAdmin):
    list_display = ["order", "name", "game", "created_at"]
    list_filter = ["game"]
    search_fields = ["name", "game__title"]
    ordering = ["game", "order"]

    fieldsets = (
        (None, {
            "fields": ("game", "order", "name", "icon_class")
        }),
    )


@admin.register(UserGameProfile)
class UserGameProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "game", "rank", "main_role", "updated_at"]
    list_filter = ["game", "created_at"]
    search_fields = ["user__username", "user__email", "game__title", "rank"]
    list_select_related = ["user", "game", "main_role"]
    autocomplete_fields = ["user", "game", "main_role"]

    fieldsets = (
        ("Profile", {
            "fields": ("user", "game")
        }),
        ("Game Data", {
            "fields": ("rank", "main_role")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ["created_at", "updated_at"]
