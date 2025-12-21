from django.urls import path

from games.views import (
    GameListView, 
    GetGameRolesView,
)

app_name = "games"

urlpatterns = [
    path("", GameListView.as_view(), name="index"),
    path("htmx/get-game-roles/", GetGameRolesView.as_view(), name="get-game-roles"),

]
