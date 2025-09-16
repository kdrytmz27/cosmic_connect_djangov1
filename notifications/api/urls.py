# notifications/api/urls.py

from django.urls import path
from .views import NotificationListView, MarkNotificationsAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('mark-as-read/', MarkNotificationsAsReadView.as_view(), name='mark-as-read'),
]