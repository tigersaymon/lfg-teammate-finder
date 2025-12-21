from django.urls import path

from games.views import (
    GameListView, 
    GetGameRolesView,
    MyGameProfilesListView,
    GameProfileCreateView,
    GameProfileUpdateView,
    GameProfileDeleteView
)

app_name = "games"

urlpatterns = [
    path("", GameListView.as_view(), name="index"),
    path("htmx/get-game-roles/", GetGameRolesView.as_view(), name="get-game-roles"),
    path("settings/games/", MyGameProfilesListView.as_view(), name="my-profiles"),
    path("settings/games/add/", GameProfileCreateView.as_view(), name="profile-create"),
    path("settings/games/<slug:game_slug>/edit/", GameProfileUpdateView.as_view(), name="profile-edit"),
    path("settings/games/<slug:game_slug>/delete/", GameProfileDeleteView.as_view(), name="profile-delete"),
]
