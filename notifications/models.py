# notifications/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NEW_LIKE = 'new_like', _('Yeni Beğeni')
        NEW_MATCH = 'new_match', _('Yeni Eşleşme')
        NEW_MESSAGE = 'new_message', _('Yeni Mesaj')
        DAILY_MATCH = 'daily_match', _('Günün Eşleşmesi')

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE, verbose_name=_("Alıcı"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_notifications', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Gönderen"))
    
    notification_type = models.CharField(_("Bildirim Tipi"), max_length=20, choices=NotificationType.choices)
    message = models.CharField(_("Mesaj"), max_length=255)
    is_read = models.BooleanField(_("Okundu mu?"), default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Bildirime tıklandığında hangi ekrana gidileceğini belirtmek için
    # Jenerik bir Foreign Key veya basit bir URL alanı kullanılabilir.
    # Şimdilik basit tutuyoruz.
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Bildirim")
        verbose_name_plural = _("Bildirimler")

    def __str__(self):
        return f"Bildirim: {self.recipient.username} - {self.get_notification_type_display()}"