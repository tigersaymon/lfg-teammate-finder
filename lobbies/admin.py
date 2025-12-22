from django.contrib import admin
from django.http import HttpRequest

from lobbies.models import Lobby


@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    list_select_related = ["host", "game"]

    list_display = [
        "title",
        "host",
        "game",
        "filled_slots",
        "status",
        "created_at"
    ]

    list_filter = ["status", "game", "created_at"]
    search_fields = ["title", "host__username", "invite_link"]
    fields = ["title", "description", "status", "host", "game", "size", "invite_link"]

    readonly_fields = [
        "invite_link",
        "created_at",
        "updated_at",
        "host",
        "game",
        "size"
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def filled_slots(self, obj: Lobby) -> str:
        return f"{obj.filled_count}/{obj.size}"

    filled_slots.short_description = "Slots"
