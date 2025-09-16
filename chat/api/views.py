# chat/api/views.py

from rest_framework import generics
from ..models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationListView(generics.ListAPIView):
    """
    Giriş yapmış kullanıcının dahil olduğu tüm sohbetleri listeler.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        # Her sohbete ait son mesajı verimli bir şekilde almak için
        # .prefetch_related() kullanıyoruz.
        return self.request.user.conversations.prefetch_related(
            'messages'
        ).all()
        
    def get_serializer_context(self):
        # Serializer'a request nesnesini göndererek mevcut kullanıcıya erişmesini sağlıyoruz.
        return {'request': self.request}

class MessageListView(generics.ListAPIView):
    """
    Belirli bir sohbete ait tüm mesajları listeler.
    """
    serializer_class = MessageSerializer
    pagination_class = None # Sohbet içinde sayfalama istemiyoruz

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        # Kullanıcının sadece kendi sohbetlerindeki mesajları görebilmesini sağla
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
        )