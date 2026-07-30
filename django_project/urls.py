from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    # User management
    path("accounts/", include("allauth.urls")),
    path('captcha/', include('captcha.urls')),
    # Local apps
    path("", include("pages.urls")),
    path('dashboard/', include('dashboard.urls')),
    path('news/', include('news.urls')),
    path('civic-flags/', include('flags.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)