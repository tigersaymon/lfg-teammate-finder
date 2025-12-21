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


class MyGameProfilesListView(LoginRequiredMixin, generic.ListView):
    model = UserGameProfile
    template_name = "games/profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return self.request.user.game_profiles.select_related("game", "main_role").order_by("-created_at")


class GameProfileCreateView(LoginRequiredMixin, generic.CreateView):
    model = UserGameProfile
    form_class = UserGameProfileForm
    template_name = "games/profile_form.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class GameProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = UserGameProfile
    form_class = UserGameProfileForm
    template_name = "games/profile_form.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_object(self, queryset=None):
        game_slug = self.kwargs.get("game_slug")
        return get_object_or_404(
            UserGameProfile,
            user=self.request.user,
            game__slug=game_slug
        )


class GameProfileDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = UserGameProfile
    template_name = "games/profile_confirm_delete.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_object(self, queryset=None):
        game_slug = self.kwargs.get("game_slug")
        return get_object_or_404(
            UserGameProfile,
            user=self.request.user,
            game__slug=game_slug
        )
