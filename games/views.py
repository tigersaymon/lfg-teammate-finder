from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic, View

from games.forms import UserGameProfileForm
from games.models import Game, GameRole, UserGameProfile


class GameListView(generic.ListView):
    model = Game
    template_name = "games/index.html"
    context_object_name = "games"


class GetGameRolesView(View):
    def get(self, request, *args, **kwargs):
        game_id = request.GET.get("game")
        roles = GameRole.objects.none()

        if game_id:
            roles = GameRole.objects.filter(game_id=game_id).order_by("order")

        return render(request, "games/partials/role_options.html", {"roles": roles})
