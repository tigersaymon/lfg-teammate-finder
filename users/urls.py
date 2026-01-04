from django.urls import path

from users.views import SignUpView

app_name = "users"

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
]
