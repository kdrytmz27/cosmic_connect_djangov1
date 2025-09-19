# Lütfen bu kodu kopyalayıp users/api/views.py dosyasının içine yapıştırın.

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .serializers import UserSerializer, RegisterSerializer, DeviceSerializer
from users.models import Device

User = get_user_model()

class CustomAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user = User.objects.select_related('profile').get(pk=user.pk)
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        headers = self.get_success_headers(serializer.data)
        
        # --- YAZIM HATASI BURADA DÜZELTİLDİ ---
        return Response({
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers) # HTTP_2_01_CREATED -> HTTP_201_CREATED

@method_decorator(never_cache, name='dispatch')
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        # --- NİHAİ ZAFER KODU KORUNDU ---
        # Django'nun auth middleware'inin önbelleğe aldığı `request.user` nesnesine
        # güvenmek yerine, her seferinde kullanıcıyı ve ilişkili profilini
        # doğrudan veritabanından, o anki en taze haliyle çekiyoruz.
        return User.objects.select_related('profile').get(pk=self.request.user.pk)

class RegisterDeviceView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fcm_token = serializer.validated_data['fcm_token']
        Device.objects.update_or_create(
            user=request.user, 
            fcm_token=fcm_token,
            defaults=serializer.validated_data
        )
        return Response({"status": "Cihaz başarıyla kaydedildi."}, status=status.HTTP_200_OK)