from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from users.forms import SignUpForm, UserSettingsForm

User = get_user_model()

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/sign_up.html"
    success_url = reverse_lazy("login")


class GeneralSettingsView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserSettingsForm
    template_name = "users/settings/general.html"
    success_url = reverse_lazy("settings-general")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)