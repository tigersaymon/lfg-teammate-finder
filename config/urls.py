from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import GeneralSettingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("users.urls", namespace="users")),
    path("settings/general/", GeneralSettingsView.as_view(), name="settings-general"),
    path("", include("games.urls", namespace="games")),
    path("lobbies/", include("lobbies.urls", namespace="lobbies")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
