# Lütfen bu kodu kopyalayıp users/api/views.py dosyasının içine yapıştırın.

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, DeviceSerializer
from users.models import Device

User = get_user_model()

class CustomAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
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
        
        # HATA BURADAYDI: HTTP_2_01_CREATED -> HTTP_201_CREATED olarak düzeltildi.
        return Response({
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user

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