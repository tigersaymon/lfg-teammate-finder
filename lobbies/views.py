from django.db.models import Count, Q, F
from django.shortcuts import render, get_object_or_404
from django.views import generic

from games.models import Game
from lobbies.models import Lobby


class LobbyListView(generic.ListView):
    model = Lobby
    context_object_name = "lobbies"
    paginate_by = 10

    def get_queryset(self):
        game_slug = self.kwargs.get("game_slug")
        self.game = get_object_or_404(Game, slug=game_slug)

        queryset = Lobby.objects.filter(
            game=self.game,
            status=Lobby.Status.SEARCHING
        ).select_related("host", "game").prefetch_related("slots")

        if self.request.GET.get("available_only"):
            queryset = queryset.annotate(
                filled_slots_count=Count("slots", filter=Q(slots__player__isnull=False))
            ).filter(filled_slots_count__lt=F("size"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["games"] = Game.objects.all()
        return context
