from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignUpForm(UserCreationForm):
    """
    Form for registering a new user.

    Extends UserCreationForm to enforce email uniqueness.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self) -> str:
        """
        Validates that the provided email address is unique across all users.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If the email is already registered.
        """
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return email


class UserSettingsForm(forms.ModelForm):
    """
    Form for updating user profile information.

    Allows users to edit their bio, discord tag, steam url and avatar.
    The email field is displayed but disabled to prevent changes via this form.
    """

    class Meta:
        model = User
        fields = ["avatar", "username", "email", "bio", "discord_tag", "steam_url"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
            "discord_tag": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "username#1234"
            }),
            "steam_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://steamcommunity.com/id/..."
            }),
            "avatar": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the form and disables the email field.
        """
        super().__init__(*args, **kwargs)

        if "email" in self.fields:
            self.fields["email"].disabled = True
            self.fields["email"].widget.attrs["class"] += " bg-light text-muted"
            self.fields["email"].help_text = "Email cannot be changed."
