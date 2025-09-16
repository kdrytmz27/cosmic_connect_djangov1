# astrology/api/serializers.py

from rest_framework import serializers
from ..models import Horoscope

class HoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horoscope
        fields = ['sign', 'get_sign_display', 'comment_type', 'date', 'prediction_data']

class AllHoroscopesSerializer(serializers.Serializer):
    """
    Kullanıcının günlük, haftalık ve aylık burç yorumlarını tek bir yapıda sunar.
    """
    daily = HoroscopeSerializer(read_only=True, allow_null=True)
    weekly = HoroscopeSerializer(read_only=True, allow_null=True)
    monthly = HoroscopeSerializer(read_only=True, allow_null=True)