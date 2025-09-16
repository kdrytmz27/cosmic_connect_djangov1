# astrology/admin.py

from django.contrib import admin
from .models import Horoscope

@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ('sign', 'comment_type', 'date', 'updated_at')
    list_filter = ('sign', 'comment_type', 'date')
    search_fields = ('prediction_data',)
    ordering = ('-date', 'sign')