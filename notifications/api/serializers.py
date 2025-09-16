# notifications/api/serializers.py

from rest_framework import serializers
from ..models import Notification
from users.api.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'get_notification_type_display',
            'message', 'is_read', 'created_at'
        ]