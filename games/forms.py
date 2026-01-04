from typing import Any

from django import forms
from django.urls import reverse

from games.models import (
    UserGameProfile,
    Game,
    GameRole
)


class UserGameProfileForm(forms.ModelForm):
    """
    Form for creating and updating a user's game profile.

    This form handles the complex logic of dependent dropdowns:
    the 'main_role' field options are dynamically updated based on the
    selected 'game' using HTMX.
    """

    class Meta:
        model = UserGameProfile
        fields = ["game", "rank", "main_role"]
        widgets = {
            "game": forms.Select(attrs={
                "class": "form-select",
            }),
            "main_role": forms.Select(attrs={"class": "form-select"}),
            "rank": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Global Elite"}),
        }

    def __init__(self, *args, user: Any = None, **kwargs) -> None:
        """
        Initializes the form with custom logic for game and role filtering.

        Args:
            user: The current user. Used to filter out games the user
                  has already added to their profile list.
        """
        super().__init__(*args, **kwargs)

        htmx_url = reverse("games:get-game-roles")

        self.fields["game"].widget.attrs.update({
            "hx-get": htmx_url,
            "hx-target": "#id_main_role",
            "hx-trigger": "change"
        })

        if user and not self.instance.pk:
            existing_game_ids = user.game_profiles.values_list("game_id", flat=True)
            self.fields["game"].queryset = Game.objects.exclude(id__in=existing_game_ids)
        elif self.instance.pk:
            self.fields["game"].disabled = True

        self.fields["game"].empty_label = "Select a game..."

        self.fields["main_role"].queryset = GameRole.objects.none()

        if "game" in self.data:
            try:
                game_id = int(self.data.get("game"))
                self.fields["main_role"].queryset = GameRole.objects.filter(game_id=game_id)
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields["main_role"].queryset = self.instance.game.roles.all()
