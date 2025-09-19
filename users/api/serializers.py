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
    sun_sign_display = serializers.CharField(source='get_sun_sign_display', read_only=True)
    moon_sign_display = serializers.CharField(source='get_moon_sign_display', read_only=True)
    rising_sign_display = serializers.CharField(source='get_rising_sign_display', read_only=True)

    # --- NİHAİ DÜZELTME: EKSİK KİŞİSEL GEZEGENLER EKLENDİ ---
    # Django, "choices" olan her alan için otomatik olarak "get_FIELD_display" metodu oluşturur.
    # Biz de bu metodları kullanarak Türkçe isimleri API'ye ekliyoruz.
    mercury_sign_display = serializers.CharField(source='get_mercury_sign_display', read_only=True)
    venus_sign_display = serializers.CharField(source='get_venus_sign_display', read_only=True)
    mars_sign_display = serializers.CharField(source='get_mars_sign_display', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'birth_date', 'birth_time', 'birth_city', 'gender', 'avatar',
            'latitude', 'longitude', 'age', 
            
            'is_birth_chart_calculated', 
            'sun_sign', 'moon_sign', 'rising_sign', 'mercury_sign', 'venus_sign', 'mars_sign', 
            'natal_chart_png_base64', 'insights_data',
            
            # Türkçe isimler için eklenen tüm alanlar
            'sun_sign_display', 'moon_sign_display', 'rising_sign_display',
            'mercury_sign_display', 'venus_sign_display', 'mars_sign_display' # EKSİK OLANLAR EKLENDİ
        ]
        
        read_only_fields = [
            'latitude', 'longitude', 'age', 'is_birth_chart_calculated',
            'sun_sign', 'moon_sign', 'rising_sign', 'mercury_sign', 'venus_sign', 'mars_sign', 
            'natal_chart_png_base64', 'insights_data', 'sun_sign_display', 'moon_sign_display', 
            'rising_sign_display', 'mercury_sign_display', 'venus_sign_display', 'mars_sign_display' # EKSİK OLANLAR EKLENDİ
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

        if 'birth_city' in update_fields:
            try:
                geolocator = Nominatim(user_agent="cosmic_connect_app", timeout=10)
                location = geolocator.geocode(profile.birth_city)
                if location:
                    profile.latitude = location.latitude
                    profile.longitude = location.longitude
                    if 'latitude' not in update_fields: update_fields.append('latitude')
                    if 'longitude' not in update_fields: update_fields.append('longitude')
            except (GeocoderTimedOut, GeocoderUnavailable):
                print(f"Uyarı: {profile.birth_city} için koordinat alınamadı.")
        
        if update_fields:
            profile.save(update_fields=update_fields)

        instance.refresh_from_db()
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