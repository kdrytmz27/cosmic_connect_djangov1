# Lütfen bu kodu kopyalayıp users/api/serializers.py dosyasının içine yapıştırın.

from rest_framework import serializers
from django.contrib.auth import get_user_model
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from users.models import Profile, Device

User = get_user_model()

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['fcm_token', 'device_type']

class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Profile
        exclude = ['user']
        read_only_fields = [
            'age', 'sun_sign', 'moon_sign', 'rising_sign', 'mercury_sign', 
            'venus_sign', 'mars_sign', 'natal_chart_png_base64', 'insights_data'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        
        update_fields = []
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
            update_fields.append(attr)

        # --- YENİ AKILLI BÖLÜM ---
        # Eğer doğum şehri güncellendiyse, koordinatları otomatik olarak bul ve ekle.
        if 'birth_city' in update_fields:
            try:
                geolocator = Nominatim(user_agent="cosmic_connect_app")
                location = geolocator.geocode(profile.birth_city, timeout=10)
                if location:
                    profile.latitude = location.latitude
                    profile.longitude = location.longitude
                    # Bu alanların da güncellendiğini listeye ekle
                    if 'latitude' not in update_fields: update_fields.append('latitude')
                    if 'longitude' not in update_fields: update_fields.append('longitude')
            except (GeocoderTimedOut, GeocoderUnavailable):
                # Eğer geocoding servisi çalışmazsa işlemi durdurma, sadece logla.
                # Daha sonra tekrar denenebilir.
                print(f"Uyarı: {profile.birth_city} için koordinat alınamadı.")
        
        if update_fields:
            profile.save(update_fields=update_fields)

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )