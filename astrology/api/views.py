# astrology/api/views.py

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Horoscope
from .serializers import AllHoroscopesSerializer

class HoroscopeView(APIView):
    """
    Giriş yapmış kullanıcının Güneş burcuna göre en güncel
    günlük, haftalık ve aylık burç yorumlarını getirir.
    """
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        sun_sign = profile.sun_sign
        
        if not sun_sign:
            return Response({'daily': None, 'weekly': None, 'monthly': None})
        
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        horoscopes = Horoscope.objects.filter(sign=sun_sign).order_by('-date')
        
        data = {
            'daily': horoscopes.filter(comment_type='daily', date__lte=today).first(),
            'weekly': horoscopes.filter(comment_type='weekly', date__lte=today, date__gte=start_of_week).first(),
            'monthly': horoscopes.filter(comment_type='monthly', date__lte=today, date__month=today.month, date__year=today.year).first()
        }
        
        serializer = AllHoroscopesSerializer(data)
        return Response(serializer.data)