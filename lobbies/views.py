from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from games.models import Game
from lobbies.forms import LobbyForm
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


class LobbyCreateView(LoginRequiredMixin, generic.CreateView):
    model = Lobby
    form_class = LobbyForm
    template_name = "lobbies/lobby_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.game = get_object_or_404(Game, slug=self.kwargs["game_slug"])
        kwargs["game"] = self.game
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context

    def form_valid(self, form):
        form.instance.host = self.request.user
        form.instance.game = self.game

        self.object = form.save()
        host_role = form.cleaned_data.get("host_role")
        if host_role:
            first_slot = self.object.slots.filter(order=1).first()
            if first_slot:
                first_slot.required_role = host_role
                first_slot.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("lobbies:lobby-list", kwargs={"game_slug": self.game.slug})
