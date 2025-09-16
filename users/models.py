# Lütfen bu kodu kopyalayıp users/models.py dosyasının içine yapıştırın.

import os
from datetime import date
from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from astrology.tasks import process_astrological_data_for_profile

SIGN_CHOICES = [
    ('Aries', _('Koç')), ('Taurus', _('Boğa')), ('Gemini', _('İkizler')),
    ('Cancer', _('Yengeç')), ('Leo', _('Aslan')), ('Virgo', _('Başak')),
    ('Libra', _('Terazi')), ('Scorpio', _('Akrep')), ('Sagittarius', _('Yay')),
    ('Capricorn', _('Oğlak')), ('Aquarius', _('Kova')), ('Pisces', _('Balık')),
]

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    first_name = None
    last_name = None
    REQUIRED_FIELDS = ['email']
    def __str__(self):
        return self.username

class Profile(models.Model):
    class Gender(models.TextChoices):
        FEMALE = 'female', _('Kadın')
        MALE = 'male', _('Erkek')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_("Kullanıcı"))
    bio = models.TextField(_("Hakkında"), max_length=500, blank=True)
    avatar = models.ImageField(_("Profil Fotoğrafı"), default='avatars/default.png', upload_to='avatars/')
    gender = models.CharField(_("Cinsiyet"), max_length=10, choices=Gender.choices, blank=True, db_index=True)
    
    birth_date = models.DateField(_("Doğum Tarihi"), null=True, blank=True, db_index=True)
    birth_time = models.TimeField(_("Doğum Saati"), null=True, blank=True)
    birth_city = models.CharField(_("Doğum Şehri"), max_length=100, blank=True)
    latitude = models.FloatField(_("Enlem"), null=True, blank=True)
    longitude = models.FloatField(_("Boylam"), null=True, blank=True)

    sun_sign = models.CharField(_("Güneş Burcu"), max_length=20, choices=SIGN_CHOICES, blank=True, db_index=True)
    moon_sign = models.CharField(_("Ay Burcu"), max_length=20, choices=SIGN_CHOICES, blank=True)
    rising_sign = models.CharField(_("Yükselen Burç"), max_length=20, choices=SIGN_CHOICES, blank=True)
    mercury_sign = models.CharField(_("Merkür Burcu"), max_length=20, choices=SIGN_CHOICES, blank=True)
    venus_sign = models.CharField(_("Venüs Burcu"), max_length=20, choices=SIGN_CHOICES, blank=True)
    mars_sign = models.CharField(_("Mars Burcu"), max_length=20, choices=SIGN_CHOICES, blank=True)
    
    natal_chart_png_base64 = models.TextField(_("Doğum Haritası (Base64)"), blank=True)
    insights_data = models.JSONField(_("Astrolojik Analiz Verileri"), null=True, blank=True)

    class Meta:
        verbose_name = _("Profil")
        verbose_name_plural = _("Profiller")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def age(self):
        if not self.birth_date: return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar and hasattr(self.avatar, 'path'):
            try:
                if not os.path.exists(self.avatar.path): return
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path, format=img.format, quality=85, optimize=True)
            except (IOError, FileNotFoundError) as e:
                print(f"Error processing avatar for {self.user.username}: {e}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def trigger_astrology_processing(sender, instance, created, update_fields, **kwargs):
    if not all([instance.birth_date, instance.birth_time, instance.birth_city, instance.latitude, instance.longitude]):
        return
    
    if not created and update_fields and not any(field in update_fields for field in ['birth_date', 'birth_time', 'birth_city']):
        return
    
    process_astrological_data_for_profile.delay(profile_id=instance.id)

class Device(models.Model):
    class DeviceType(models.TextChoices):
        ANDROID = 'android', _('Android')
        IOS = 'ios', _('iOS')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices', verbose_name=_("Kullanıcı"))
    fcm_token = models.TextField(_("Firebase Cloud Messaging Token"))
    device_type = models.CharField(_("Cihaz Tipi"), max_length=10, choices=DeviceType.choices, default=DeviceType.ANDROID)
    is_active = models.BooleanField(_("Aktif mi?"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _("Cihaz")
        verbose_name_plural = _("Cihazlar")
        unique_together = ('user', 'fcm_token')
        ordering = ['-updated_at']
    def __str__(self):
        return f"{self.user.username}'s Device ({self.get_device_type_display()})"