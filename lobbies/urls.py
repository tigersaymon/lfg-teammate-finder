from django.urls import path
from .views import LobbyListView


app_name = "lobbies"

urlpatterns = [
    path("/<slug:game_slug>/", LobbyListView.as_view(), name="lobby_list"),
]