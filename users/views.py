from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import generic

from users.forms import SignUpForm

User = get_user_model()

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/sign_up.html"
    success_url = reverse_lazy("login")
