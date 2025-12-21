from django.urls import path

from games.views import (
    GameListView, 
    GetGameRolesView,
    MyGameProfilesListView,
)

app_name = "games"

urlpatterns = [
    path("", GameListView.as_view(), name="index"),
    path("htmx/get-game-roles/", GetGameRolesView.as_view(), name="get-game-roles"),
    path("settings/games/", MyGameProfilesListView.as_view(), name="my-profiles"),

]
