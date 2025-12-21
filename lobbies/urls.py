from django.urls import path
from .views import LobbyListView, LobbyCreateView

app_name = "lobbies"

urlpatterns = [
    path("<slug:game_slug>/", LobbyListView.as_view(), name="lobby-list"),
    path("<slug:game_slug>/create/", LobbyCreateView.as_view(), name="lobby-create"),
]