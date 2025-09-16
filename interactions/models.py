# interactions/models.py

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class InteractionManager(models.Manager):
    def for_users(self, user1, user2):
        """İki kullanıcı arasındaki etkileşimi, sıradan bağımsız olarak bulur."""
        if user1.id > user2.id:
            user1, user2 = user2, user1
        return self.get_queryset().filter(user1=user1, user2=user2)

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InteractionManager()

    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = _("Eşleşme")
        verbose_name_plural = _("Eşleşmeler")

class Like(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='given_likes', on_delete=models.CASCADE, verbose_name=_("Beğenen"))
    liked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_likes', on_delete=models.CASCADE, verbose_name=_("Beğenilen"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('liker', 'liked')
        verbose_name = _("Beğeni")
        verbose_name_plural = _("Beğeniler")

class SuperLike(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='given_super_likes', on_delete=models.CASCADE, verbose_name=_("Süper Beğenen"))
    liked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_super_likes', on_delete=models.CASCADE, verbose_name=_("Süper Beğenilen"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('liker', 'liked')
        verbose_name = _("Süper Beğeni")
        verbose_name_plural = _("Süper Beğeniler")

class Block(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='given_blocks', on_delete=models.CASCADE, verbose_name=_("Engelleyen"))
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_blocks', on_delete=models.CASCADE, verbose_name=_("Engellenen"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')
        verbose_name = _("Engelleme")
        verbose_name_plural = _("Engellemeler")

class Compatibility(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='compatibilities1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='compatibilities2', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0, verbose_name=_("Skor"))
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = InteractionManager()

    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = _("Uyumluluk")
        verbose_name_plural = _("Uyumluluklar")

class DailyMatch(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_match', verbose_name=_("Kullanıcı"))
    matched_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_match_for', verbose_name=_("Eşleştiği Kullanıcı"))
    date = models.DateField(default=timezone.now, db_index=True)

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = _("Günün Eşleşmesi")
        verbose_name_plural = _("Günün Eşleşmeleri")