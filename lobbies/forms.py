from django import forms

from games.models import GameRole
from .models import Lobby


class LobbyForm(forms.ModelForm):
    host_role = forms.ModelChoiceField(
        queryset=GameRole.objects.none(),
        required=False,
        label="Your role",
        empty_label="Flex",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    class Meta:
        model = Lobby
        fields = ["title", "description", "size", "communication_link", "is_public"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Ranked 5000+ MMR"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "size": forms.NumberInput(attrs={
                "class": "form-control",
            }),
            "communication_link": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://discord.gg/..."
            }),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.game = kwargs.pop("game", None)
        super().__init__(*args, **kwargs)

        if self.game:
            self.fields["host_role"].queryset = GameRole.objects.filter(game=self.game)

            max_size = min(self.game.team_size * 2, 20)

            self.fields["size"].widget.attrs.update({
                "min": 2,
                "max": max_size,
                "value": self.game.team_size
            })
            self.fields["size"].help_text = f"Standard for {self.game.title}: {self.game.team_size} players."

    def clean_size(self):
        size = self.cleaned_data["size"]
        if self.game and size > self.game.team_size * 2:
            raise forms.ValidationError(f"Too many players for {self.game.title}")
        return size

