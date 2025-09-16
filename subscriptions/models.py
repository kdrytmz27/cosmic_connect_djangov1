# subscriptions/models.py

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class SubscriptionPlan(models.Model):
    """
    Uygulamadaki farklı abonelik paketlerini tanımlar (örn: Altın, Platin).
    """
    name = models.CharField(_("Paket Adı"), max_length=100)
    product_id_apple = models.CharField(_("Apple Product ID"), max_length=255, unique=True, help_text=_("App Store Connect'teki Ürün ID'si"))
    product_id_google = models.CharField(_("Google Product ID"), max_length=255, unique=True, help_text=_("Google Play Console'daki Ürün ID'si"))
    duration_days = models.PositiveIntegerField(_("Süre (Gün)"), help_text=_("Bu paketin kaç gün geçerli olduğu"))
    is_active = models.BooleanField(_("Aktif mi?"), default=True)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    """
    Bir kullanıcının aktif abonelik durumunu ve süresini takip eder.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='subscription', on_delete=models.CASCADE, verbose_name=_("Kullanıcı"))
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Abonelik Paketi"))
    start_date = models.DateTimeField(_("Başlangıç Tarihi"))
    end_date = models.DateTimeField(_("Bitiş Tarihi"), db_index=True)
    is_active = models.BooleanField(_("Aktif mi?"), default=True, db_index=True)
    
    class Meta:
        verbose_name = _("Kullanıcı Aboneliği")
        verbose_name_plural = _("Kullanıcı Abonelikleri")

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'Paket Yok'}"
        
class Purchase(models.Model):
    class Store(models.TextChoices):
        APPLE_APP_STORE = 'apple', _('Apple App Store')
        GOOGLE_PLAY = 'google', _('Google Play Store')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases', verbose_name=_("Kullanıcı"))
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, verbose_name=_("Satın Alınan Paket"))
    store = models.CharField(_("Mağaza"), max_length=10, choices=Store.choices)
    transaction_id = models.CharField(_("İşlem ID"), max_length=255, unique=True)
    purchase_token = models.TextField(_("Satın Alma Token'ı"))
    purchase_date = models.DateTimeField(_("Satın Alma Tarihi"))
    is_verified = models.BooleanField(_("Doğrulandı mı?"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = _("Satın Alma İşlemi")
        verbose_name_plural = _("Satın Alma İşlemleri")

    def __str__(self):
        return f"Purchase by {self.user.username} on {self.purchase_date.strftime('%Y-%m-%d')}"