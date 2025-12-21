from django.urls import path
from .views import (
    LobbyListView,
    LobbyCreateView,
    LobbyDetailView,
    LobbyDeleteView,
    JoinSlotView,
    LeaveSlotView
)

app_name = "lobbies"

urlpatterns = [
    path("<slug:game_slug>/", LobbyListView.as_view(), name="lobby-list"),
    path("<slug:game_slug>/create/", LobbyCreateView.as_view(), name="lobby-create"),
    path("<slug:game_slug>/<uuid:invite_link>/", LobbyDetailView.as_view(), name="lobby-detail"),
    path("<slug:game_slug>/<uuid:invite_link>/delete/", LobbyDeleteView.as_view(), name="lobby-delete"),
    path("<slug:game_slug>/<uuid:invite_link>/join/<int:slot_id>/", JoinSlotView.as_view(), name="lobby-join"),
    path("<slug:game_slug>/<uuid:invite_link>/leave/<int:slot_id>/", LeaveSlotView.as_view(), name="lobby-leave"),
]