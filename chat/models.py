# chat/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone  # <<< --- EKSİK OLAN İMPORT BURAYA EKLENDİ ---
from django.utils.translation import gettext_lazy as _

class ConversationManager(models.Manager):
    def get_or_create_for_users(self, user1, user2):
        """
        Verilen iki kullanıcı için bir sohbeti bulur veya oluşturur.
        Performans için kullanıcı ID'lerini sıralayarak tutarlı bir sorgu yapar.
        """
        if user1.id > user2.id:
            user1, user2 = user2, user1
            
        queryset = self.get_queryset().filter(participants=user1).filter(participants=user2)
        if queryset.exists():
            return queryset.first(), False
        else:
            conversation = self.create()
            conversation.participants.add(user1, user2)
            return conversation, True

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations', verbose_name=_("Katılımcılar"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ConversationManager()

    class Meta:
        ordering = ['-updated_at']
        verbose_name = _("Sohbet")
        verbose_name_plural = _("Sohbetler")

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE, verbose_name=_("Sohbet"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE, verbose_name=_("Gönderen"))
    content = models.TextField(_("İçerik"))
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(_("Okundu mu?"), default=False)
    
    class Meta: 
        ordering = ['timestamp']
        verbose_name = _("Mesaj")
        verbose_name_plural = _("Mesajlar")

    def save(self, *args, **kwargs):
        """
        Mesaj kaydedildiğinde, ait olduğu sohbetin 'updated_at' alanını günceller.
        """
        # Sohbetin güncellenme zamanını ayarla
        # timestamp alanı auto_now_add olduğu için ilk kayıtta None olabilir.
        # Bu yüzden timezone.now() ile güvenli bir atama yapıyoruz.
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at']) # Sadece tek bir alanı güncelle, daha verimli.
        super().save(*args, **kwargs)