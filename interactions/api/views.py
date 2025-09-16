# interactions/api/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import Compatibility, DailyMatch, Like, Match, Block, SuperLike
from .serializers import CompatibilitySerializer, DailyMatchSerializer
from users.models import Profile

User = get_user_model()

class DiscoverView(generics.ListAPIView):
    """
    Kullanıcıya en uyumlu profilleri, sayfalanmış olarak sunar.
    """
    serializer_class = CompatibilitySerializer

    def get_queryset(self):
        user = self.request.user
        
        blocked_by_user = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
        user_blocked_by = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
        excluded_ids = set(blocked_by_user) | set(user_blocked_by) | {user.id}
        
        queryset = Compatibility.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).exclude(
            Q(user1_id__in=excluded_ids) | Q(user2_id__in=excluded_ids)
        ).order_by('-score')
        
        return queryset

class DailyMatchView(generics.RetrieveAPIView):
    serializer_class = DailyMatchSerializer
    
    def get_object(self):
        return get_object_or_404(
            DailyMatch, 
            user=self.request.user, 
            date=timezone.now().date()
        )

class LikeView(APIView):
    def post(self, request, user_id, *args, **kwargs):
        liker = request.user
        try:
            liked = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        if Like.objects.filter(liker=liker, liked=liked).exists():
            return Response({"error": "Kullanıcı zaten beğenilmiş."}, status=status.HTTP_400_BAD_REQUEST)
        
        Like.objects.create(liker=liker, liked=liked)

        is_match = Like.objects.filter(liker=liked, liked=liker).exists()
        if is_match:
            user1, user2 = sorted([liker, liked], key=lambda u: u.id)
            Match.objects.get_or_create(user1=user1, user2=user2)
            # Burada Match bildirimi gönderilebilir.
        
        return Response({"status": "Beğeni başarılı.", "is_match": is_match}, status=status.HTTP_201_CREATED)