from django.shortcuts import render
from django.views import generic

from games.models import Game


class GameListView(generic.ListView):
    model = Game
    template_name = "games/index.html"
    context_object_name = "games"
