# subscriptions/api/serializers.py

from rest_framework import serializers
from ..models import Purchase

class PurchaseVerificationSerializer(serializers.Serializer):
    """
    Mobil uygulamadan gelen satın alma doğrulama isteğinin verisini doğrular.
    """
    store = serializers.ChoiceField(choices=Purchase.Store.choices)
    product_id = serializers.CharField(max_length=255)
    purchase_token = serializers.CharField()
    transaction_id = serializers.CharField(max_length=255)