from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/notes/", include("apps.notes.urls")),
    path("api/social/", include("apps.social.urls")),
    path("api/search/", include("apps.search.urls")),
    path("api/messaging/", include("apps.messaging.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
