# Lütfen bu kodu kopyalayıp interactions/api/serializers.py dosyasının içine yapıştırın.

from rest_framework import serializers
from users.api.serializers import UserSerializer
from ..models import DailyMatch, Compatibility

class CompatibilitySerializer(serializers.ModelSerializer):
    """
    Discover ekranı için ana serializer.
    Uyumluluk skorunu, dökümünü ve diğer kullanıcının profilini içerir.
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = Compatibility
        # --- FAZ 2 DEĞİŞİKLİĞİ: 'breakdown' alanı eklendi ---
        fields = ['user', 'score', 'breakdown']

    def get_user(self, obj):
        # Serializer'ın context'inden isteği yapan kullanıcıyı al
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return None # veya hata fırlat
        
        request_user = request.user
        
        # Uyumluluk nesnesindeki diğer kullanıcıyı bul
        other_user = obj.user2 if obj.user1 == request_user else obj.user1
        
        # Diğer kullanıcının verisini UserSerializer ile serileştir
        return UserSerializer(other_user).data

class DailyMatchSerializer(serializers.ModelSerializer):
    matched_user = UserSerializer(read_only=True)

    class Meta:
        model = DailyMatch
        fields = ['date', 'matched_user']

class ActivityDataSerializer(serializers.Serializer):
    """
    Kullanıcının beğeni, eşleşme ve super beğeni sayılarını serileştirir.
    """
    likes_count = serializers.IntegerField()
    matches_count = serializers.IntegerField()
    superlikes_count = serializers.IntegerField()