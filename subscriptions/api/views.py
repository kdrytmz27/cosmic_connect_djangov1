# subscriptions/api/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .serializers import PurchaseVerificationSerializer
from ..models import Purchase, SubscriptionPlan
from ..logic import grant_premium_access

class VerifyPurchaseView(APIView):
    """
    Apple/Google'dan gelen satın alma token'ını doğrular ve kullanıcıya premium erişim verir.
    NOT: Bu, basit bir başlangıç noktasıdır. Gerçek dünyada, sunucu tarafında
    Apple/Google API'leri ile bu token'ın gerçekten geçerli olup olmadığını
    kontrol eden bir mantık eklenmelidir (örn: `google-auth` veya `requests` kütüphaneleri ile).
    """
    def post(self, request, *args, **kwargs):
        serializer = PurchaseVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 1. Gelen Product ID'ye göre abonelik planını bul
        try:
            if data['store'] == 'apple':
                plan = SubscriptionPlan.objects.get(product_id_apple=data['product_id'])
            else: # google
                plan = SubscriptionPlan.objects.get(product_id_google=data['product_id'])
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Geçersiz ürün ID'si."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Satın alma işleminin daha önce kaydedilip kaydedilmediğini kontrol et
        if Purchase.objects.filter(transaction_id=data['transaction_id']).exists():
            return Response({"error": "Bu işlem daha önce kaydedilmiş."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Her şey yolundaysa, işlemi veritabanına kaydet ve premium erişim ver
        with transaction.atomic():
            # Satın alma işlemini kaydet
            purchase = Purchase.objects.create(
                user=request.user,
                plan=plan,
                store=data['store'],
                transaction_id=data['transaction_id'],
                purchase_token=data['purchase_token'],
                purchase_date=timezone.now(),
                is_verified=True # Şimdilik otomatik doğrulandı kabul ediyoruz
            )
            # Kullanıcıya premium hakkı tanı
            grant_premium_access(request.user, plan)

        return Response({"status": "Satın alma başarıyla doğrulandı."}, status=status.HTTP_200_OK)