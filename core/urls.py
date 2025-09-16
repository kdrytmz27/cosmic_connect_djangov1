# core/urls.py (Nihai ve Tam Hali)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Tüm API uygulamaları burada listeleniyor
api_v1_patterns = [
    path('users/', include('users.api.urls')),
    path('astrology/', include('astrology.api.urls')),
    path('interactions/', include('interactions.api.urls')),
    path('chat/', include('chat.api.urls')),
    path('notifications/', include('notifications.api.urls')), # EKLENDİ
    path('subscriptions/', include('subscriptions.api.urls')), # EKLENDİ
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)