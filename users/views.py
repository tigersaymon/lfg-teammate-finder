from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic

from users.forms import SignUpForm, UserSettingsForm

User = get_user_model()


class SignUpView(generic.CreateView):
    """
    View for standard user registration.

    Handles the display and processing of the SignUpForm.
    Redirects to the login page upon successful registration.
    """
    form_class = SignUpForm
    template_name = "registration/sign_up.html"
    success_url = reverse_lazy("login")


class GeneralSettingsView(LoginRequiredMixin, generic.UpdateView):
    """
    View for updating the current user's general profile settings.

    Uses UserSettingsForm to allow editing of non-sensitive data.
    Overrides get_object to target the currently logged-in user.
    """
    model = User
    form_class = UserSettingsForm
    template_name = "users/settings/general.html"
    success_url = reverse_lazy("settings-general")

    def get_object(self, queryset: QuerySet | None = None) -> User:
        """
        Returns the user object associated with the current request.

        This ensures users can only edit their own profile, ignoring
        any PKs passed in the URL.
        """
        return self.request.user

    def form_valid(self, form: UserSettingsForm) -> HttpResponse:
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)
