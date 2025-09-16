# astrology/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import SIGN_CHOICES # SIGN_CHOICES'ı merkezi yerden alıyoruz

class Horoscope(models.Model):
    class CommentType(models.TextChoices):
        DAILY = 'daily', _('Günlük')
        WEEKLY = 'weekly', _('Haftalık')
        MONTHLY = 'monthly', _('Aylık')

    sign = models.CharField(_("Burç"), max_length=20, choices=SIGN_CHOICES, db_index=True)
    comment_type = models.CharField(_("Yorum Tipi"), max_length=10, choices=CommentType.choices, db_index=True)
    date = models.DateField(_("Tarih"), db_index=True)
    prediction_data = models.JSONField(_("Tahmin Verisi"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Burç Yorumu")
        verbose_name_plural = _("Burç Yorumları")
        unique_together = ('sign', 'comment_type', 'date')
        ordering = ['-date', 'sign']

    def __str__(self):
        return f"{self.get_sign_display()} - {self.get_comment_type_display()} ({self.date})"