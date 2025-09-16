# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.html import escape
from .models import Message, Conversation
from users.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        is_participant = await self.check_participation()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
        await self.accept()
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.conversation_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = escape(data.get('message', '')).strip()

        if not message_content:
            return

        message = await self.save_message(message_content)
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender_id': self.user.id,
                'timestamp': message.timestamp.isoformat(),
            }
        )
        # Burada yeni mesaj için bildirim görevi tetiklenebilir.

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))
        
    @database_sync_to_async
    def check_participation(self):
        return Conversation.objects.filter(id=self.conversation_id, participants=self.user).exists()

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(sender=self.user, conversation=conversation, content=content)

    @database_sync_to_async
    def mark_messages_as_read(self):
        Conversation.objects.get(id=self.conversation_id).messages.filter(
            is_read=False
        ).exclude(
            sender=self.user
        ).update(is_read=True)