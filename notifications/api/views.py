# notifications/api/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """
    Giriş yapmış kullanıcının tüm bildirimlerini listeler.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.all()

class MarkNotificationsAsReadView(APIView):
    """
    Kullanıcının okunmamış tüm bildirimlerini okundu olarak işaretler.
    """
    def post(self, request, *args, **kwargs):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)