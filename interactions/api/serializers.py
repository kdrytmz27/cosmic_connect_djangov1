# interactions/api/serializers.py

from rest_framework import serializers
from users.api.serializers import UserSerializer # Yeniden kullanılabilir UserSerializer
from ..models import DailyMatch, Compatibility

class CompatibilitySerializer(serializers.ModelSerializer):
    """
    Discover ekranı için ana serializer.
    Uyumluluk skorunu ve diğer kullanıcının profilini içerir.
    """
    # Diğer kullanıcıyı (user2) tam profil bilgisiyle göster
    user = serializers.SerializerMethodField()

    class Meta:
        model = Compatibility
        fields = ['user', 'score']

    def get_user(self, obj):
        # Bu serializer'ı çağıran view'deki context'ten mevcut kullanıcıyı al
        request_user = self.context.get('request').user
        # Uyumluluk nesnesindeki diğer kullanıcıyı bul
        other_user = obj.user2 if obj.user1 == request_user else obj.user1
        # Diğer kullanıcının verisini UserSerializer ile formatla
        return UserSerializer(other_user).data

class DailyMatchSerializer(serializers.ModelSerializer):
    matched_user = UserSerializer(read_only=True)

    class Meta:
        model = DailyMatch
        fields = ['date', 'matched_user']