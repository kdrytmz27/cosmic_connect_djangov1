# subscriptions/api/urls.py

from django.urls import path
from .views import VerifyPurchaseView

urlpatterns = [
    path('verify-purchase/', VerifyPurchaseView.as_view(), name='verify-purchase'),
]