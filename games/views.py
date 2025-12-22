from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic, View

from games.forms import UserGameProfileForm
from games.models import Game, GameRole, UserGameProfile


class GameListView(generic.ListView):
    """
    Displays a catalog of all supported games.

    This view serves as the entry point for users to explore available games
    and proceed to create profiles or find lobbies.
    """
    model = Game
    template_name = "games/index.html"
    context_object_name = "games"


class GetGameRolesView(View):
    """
    HTMX-specific view to fetch role options dynamically.

    This view is triggered when a user selects a game in the profile form.
    It returns a partial HTML template containing <option> tags for the
    roles associated with the selected game.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles GET requests to return role options.

        Args:
            request: The HTTP request containing the 'game' ID in GET parameters.

        Returns:
            HttpResponse: Rendered partial HTML with role options.
        """
        game_id = request.GET.get("game")
        roles = GameRole.objects.none()

        if game_id:
            roles = GameRole.objects.filter(game_id=game_id).order_by("order")

        return render(request, "games/partials/role_options.html", {"roles": roles})


class MyGameProfilesListView(LoginRequiredMixin, generic.ListView):
    """
    Displays the dashboard of game profiles created by the current user.
    """
    model = UserGameProfile
    template_name = "games/profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self) -> QuerySet[UserGameProfile]:
        """
        Retrieves profiles belonging ONLY to the current user.

        Optimizes database access by selecting related 'game' and 'main_role'
        objects to prevent N+1 query issues in the template.
        """
        return self.request.user.game_profiles.select_related(
            "game", "main_role"
        ).order_by("-created_at")


class GameProfileCreateView(LoginRequiredMixin, generic.CreateView):
    """
    Handles the creation of a new user game profile.
    """
    model = UserGameProfile
    form_class = UserGameProfileForm
    template_name = "games/profile_form.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_form_kwargs(self) -> dict:
        """
        Injects the current user instance into the form initialization.

        This allows the form to filter out games for which the user
        already has a profile.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: UserGameProfileForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)


class GameProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    """
    Handles updates to an existing game profile (e.g., changing rank or role).
    """
    model = UserGameProfile
    form_class = UserGameProfileForm
    template_name = "games/profile_form.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_object(self, queryset: QuerySet | None = None) -> UserGameProfile:
        """
        Retrieves the profile securely using the game slug and current user.

        Ensures that users can only update their own profiles, preventing
        ID enumeration attacks.
        """
        game_slug = self.kwargs.get("game_slug")
        return get_object_or_404(
            UserGameProfile,
            user=self.request.user,
            game__slug=game_slug
        )


class GameProfileDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    Handles the deletion of a user's game profile.
    """
    model = UserGameProfile
    template_name = "games/profile_confirm_delete.html"
    success_url = reverse_lazy("games:my-profiles")

    def get_object(self, queryset: QuerySet | None = None) -> UserGameProfile:
        """
        Retrieves the profile securely, ensuring ownership before deletion.
        """
        game_slug = self.kwargs.get("game_slug")
        return get_object_or_404(
            UserGameProfile,
            user=self.request.user,
            game__slug=game_slug
        )
