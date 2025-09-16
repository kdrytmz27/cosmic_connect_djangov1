# chat/api/serializers.py

from rest_framework import serializers
from ..models import Conversation, Message
from users.api.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    # Mevcut kullanıcı dışındaki diğer katılımcıyı/katılımcıları döndür
    other_participant = serializers.SerializerMethodField()
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'other_participant', 'last_message', 'updated_at']
        
    def get_other_participant(self, obj):
        request_user = self.context.get('request').user
        other_user = obj.participants.exclude(id=request_user.id).first()
        if other_user:
            return UserSerializer(other_user).data
        return None