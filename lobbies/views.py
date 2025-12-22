from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count, Q, F
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View

from games.models import Game, UserGameProfile
from lobbies.forms import LobbyForm
from lobbies.models import Lobby, Slot


class HTMXRedirect(HttpResponse):
    def __init__(self, redirect_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = redirect_to
        self.status_code = 200


class LobbyListView(generic.ListView):
    model = Lobby
    context_object_name = "lobbies"
    paginate_by = 10

    def get_queryset(self):
        game_slug = self.kwargs.get("game_slug")
        self.game = get_object_or_404(Game, slug=game_slug)
        user = self.request.user

        queryset = Lobby.objects.filter(
            game=self.game,
            status=Lobby.Status.SEARCHING
        )

        if user.is_authenticated:
            queryset = queryset.filter(
                Q(is_public=True) |
                Q(host=user) |
                Q(slots__player=user)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)

        queryset = queryset.select_related(
            "host", "game"
        ).annotate(
            filled_slots_count=Count("slots", filter=Q(slots__player__isnull=False))
        ).prefetch_related(
            "slots__player",
            "slots__required_role"
        ).order_by('-created_at')

        if self.request.GET.get("available_only"):
            queryset = queryset.filter(filled_slots_count__lt=F("size"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        # context["games"] = Game.objects.all()
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

        with transaction.atomic():
            self.object = form.save()

            host_role = form.cleaned_data.get("host_role")
            if host_role:
                self.object.slots.filter(order=1).update(required_role=host_role)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("lobbies:lobby-list", kwargs={"game_slug": self.game.slug})

    def dispatch(self, request, *args, **kwargs):
        game_slug = self.kwargs.get("game_slug")
        game = get_object_or_404(Game, slug=game_slug)

        if request.user.is_authenticated and not request.user.game_profiles.filter(game=game).exists():
            messages.warning(
                request,
                f"You need to set up your <b>{game.title}</b> profile before creating a lobby."
            )
            return redirect("games:profile-create")

        return super().dispatch(request, *args, **kwargs)


class LobbyDetailView(generic.DetailView):
    model = Lobby
    context_object_name = "lobby"
    slug_url_kwarg = "invite_link"
    slug_field = "invite_link"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "game", "host"
        ).prefetch_related(
            "slots__player"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lobby = self.object

        player_ids = [slot.player.id for slot in lobby.slots.all() if slot.player]

        profiles = UserGameProfile.objects.filter(
            user_id__in=player_ids,
            game=lobby.game
        ).select_related("main_role")

        profiles_dict = {p.user_id: p for p in profiles}

        context["profiles_dict"] = profiles_dict

        if self.request.user.is_authenticated:
            context['user_is_in_lobby'] = self.request.user.id in player_ids

        return context


class LobbyDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Lobby
    template_name = "lobbies/lobby_confirm_delete.html"
    slug_url_kwarg = "invite_link"
    slug_field = "invite_link"

    def get_object(self, queryset=None):
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        return self.get_object().host == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "lobbies:lobby-list",
            kwargs={"game_slug": self.get_object().game.slug}
        )


class SlotActionMixin:
    def _get_locked_slot(self, slot_id, invite_link):
        return get_object_or_404(
            Slot.objects.select_for_update().select_related('lobby'),
            id=slot_id,
            lobby__invite_link=invite_link
        )

    def _redirect_to_lobby(self, game_slug, invite_link):
        return redirect("lobbies:lobby-detail", game_slug=game_slug, invite_link=invite_link)

    def _handle_error(self, request, message, game_slug, invite_link):
        messages.error(request, message)

        if request.headers.get("HX-Request"):
            target_url = reverse("lobbies:lobby-detail", kwargs={
                "game_slug": game_slug,
                "invite_link": invite_link
            })
            return HTMXRedirect(target_url)

        return self._redirect_to_lobby(game_slug, invite_link)


class JoinSlotView(LoginRequiredMixin, SlotActionMixin, View):
    def post(self, request, game_slug, invite_link, slot_id):
        with transaction.atomic():
            slot = self._get_locked_slot(slot_id, invite_link)
            lobby = slot.lobby

            if not request.user.game_profiles.filter(game=lobby.game).exists():
                error_msg = f"You need a {lobby.game.title} profile to join!"
                messages.warning(request, error_msg)

                if request.headers.get("HX-Request"):
                    response = HttpResponse(status=204)
                    response["HX-Redirect"] = reverse("games:profile-create")
                    return response

                return redirect("games:profile-create")

            can_join, reason = lobby.can_join(request.user)
            if not can_join:
                return self._handle_error(request, reason, game_slug, invite_link)

            if not slot.is_available:
                return self._handle_error(
                    request, "This slot is already taken", game_slug, invite_link
                )

            slot.player = request.user
            slot.save()

            messages.success(request, f"You joined as {slot.role_name}!")

            if request.headers.get("HX-Request"):

                player_profile = request.user.game_profiles.filter(game=lobby.game).first()

                return render(request, "lobbies/partials/slot_card.html", {
                    "slot": slot,
                    "lobby": lobby,
                    "user": request.user,
                    "profile": player_profile
                })

        return self._redirect_to_lobby(game_slug, invite_link)


class LeaveSlotView(LoginRequiredMixin, SlotActionMixin, View):
    def post(self, request, game_slug, invite_link, slot_id):
        with transaction.atomic():
            slot = self._get_locked_slot(slot_id, invite_link)
            lobby = slot.lobby

            if slot.player != request.user:
                messages.error(request, "You cannot leave a slot that isn't yours.")
                return self._redirect_to_lobby(game_slug, invite_link)

            if lobby.host == request.user:
                messages.error(request, "The host cannot leave. You must delete the lobby.")
                return self._redirect_to_lobby(game_slug, invite_link)

            slot.player = None
            slot.save()

            messages.success(request, "You have left the lobby.")

            if request.headers.get("HX-Request"):
                return render(request, "lobbies/partials/slot_card.html", {
                    "slot": slot,
                    "lobby": lobby,
                    "user": request.user
                })

        return self._redirect_to_lobby(game_slug, invite_link)


class KickPlayerView(LoginRequiredMixin, SlotActionMixin, View):
    def post(self, request, game_slug, invite_link, slot_id):
        with transaction.atomic():
            slot = get_object_or_404(
                Slot.objects.select_related("lobby", "player"),
                id=slot_id,
                lobby__invite_link=invite_link
            )
            lobby = slot.lobby

            if request.user != lobby.host:
                return HttpResponseForbidden("You are not the host.")

            if slot.player == request.user:
                return HttpResponse(status=204)

            kicked_user_name = slot.player.username
            slot.player = None
            slot.save()

            messages.success(request, f"Kicked {kicked_user_name} from the lobby.")

            if request.headers.get("HX-Request"):
                return render(request, "lobbies/partials/slot_card.html", {
                    "slot": slot,
                    "lobby": lobby,
                    "user": request.user,
                    "profile": None
                })

        return self._redirect_to_lobby(game_slug, invite_link)


class ToggleLobbyPrivacyView(LoginRequiredMixin, View):
    def post(self, request, game_slug, invite_link):
        lobby = get_object_or_404(Lobby, invite_link=invite_link, host=request.user)

        lobby.is_public = not lobby.is_public
        lobby.save()

        status_msg = "Lobby is now PUBLIC" if lobby.is_public else "Lobby is now PRIVATE"
        messages.success(request, status_msg)

        return render(request, "lobbies/partials/lobby_controls.html", {
            "lobby": lobby,
            "user": request.user
        })
