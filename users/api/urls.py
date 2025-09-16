# users/api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomAuthTokenView.as_view(), name='login'),
    path('me/', views.UserProfileView.as_view(), name='me'),
    path('devices/register/', views.RegisterDeviceView.as_view(), name='device-register'),
]