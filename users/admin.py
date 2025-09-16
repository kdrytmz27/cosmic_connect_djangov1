# Lütfen bu kodu kopyalayıp users/admin.py dosyasının içine yapıştırın.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Device

class CustomUserAdmin(UserAdmin):
    """
    Özel User modelimiz için admin panelini yapılandırır.
    """
    # Admin panelinde kullanıcı listesinde gösterilecek alanlar
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    # Kullanıcı listesinde sağda filtreleme çubuğu oluşturacak alanlar
    list_filter = ('is_staff', 'is_active', 'date_joined')
    # Arama çubuğunun hangi alanlarda arama yapacağı
    search_fields = ('username', 'email')
    # Kullanıcı detay sayfasında alanların nasıl gruplanacağı
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}), # first_name ve last_name buradan kaldırıldı
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_date', 'sun_sign', 'moon_sign', 'rising_sign')
    search_fields = ('user__username', 'user__email')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'updated_at')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__username',)

# Modellerimizi admin paneline kaydediyoruz
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Device, DeviceAdmin)