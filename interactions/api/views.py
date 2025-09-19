# Lütfen bu kodu kopyalayıp interactions/api/views.py dosyasının içine yapıştırın.

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import Compatibility, DailyMatch, Like, Match, Block, SuperLike, Pass
from .serializers import CompatibilitySerializer, DailyMatchSerializer
from users.models import Profile

User = get_user_model()

class DiscoverProfilesView(generics.ListAPIView):
    """
    Kullanıcıya en uyumlu profilleri, sayfalanmış olarak sunar.
    """
    serializer_class = CompatibilitySerializer

    def get_queryset(self):
        user = self.request.user
        
        # Hariç tutulacak kullanıcıların ID'lerini topla (beğenilen, geçilen, eşleşilen, engellenen)
        liked_user_ids = set(user.given_likes.values_list('liked_id', flat=True))
        passed_user_ids = set(user.given_passes.values_list('passed_id', flat=True))
        matched_users = Match.objects.for_user(user).values_list('user1_id', 'user2_id')
        matched_user_ids = {u_id for pair in matched_users for u_id in pair if u_id != user.id}
        blocked_by_user_ids = set(Block.objects.filter(blocker=user).values_list('blocked_id', flat=True))
        user_blocked_by_ids = set(Block.objects.filter(blocked=user).values_list('blocker_id', flat=True))

        # Kendisini hariç tutmasına gerek yok, çünkü aşağıdaki mantık bunu zaten sağlıyor.
        excluded_ids = liked_user_ids | passed_user_ids | matched_user_ids | \
                       blocked_by_user_ids | user_blocked_by_ids

        # --- NİHAİ VE DOĞRU FİLTRELEME MANTIĞI ---
        queryset = Compatibility.objects.filter(
            # Mevcut kullanıcıyı içeren TÜM uyumlulukları al
            Q(user1=user) | Q(user2=user),
            # Her iki kullanıcının da haritasının hesaplandığından emin ol
            user1__profile__is_birth_chart_calculated=True,
            user2__profile__is_birth_chart_calculated=True
        ).exclude(
            # ŞİMDİ DOĞRU FİLTRELEME:
            # EĞER user1 mevcut kullanıcı ise, user2'nin hariç tutulanlarda olup olmadığını kontrol et
            Q(user1=user, user2_id__in=excluded_ids) |
            # VEYA EĞER user2 mevcut kullanıcı ise, user1'in hariç tutulanlarda olup olmadığını kontrol et
            Q(user2=user, user1_id__in=excluded_ids)
        ).select_related('user1__profile', 'user2__profile').order_by('-score')
        
        return queryset

# --- BU DOSYANIN GERİ KALANINDA BİR DEĞİŞİKLİK YOK ---

class DailyMatchView(generics.RetrieveAPIView):
    serializer_class = DailyMatchSerializer
    def get_object(self):
        return get_object_or_404(
            DailyMatch, 
            user=self.request.user, 
            date=timezone.now().date()
        )

class ActivityDataView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        matched_users = Match.objects.for_user(user).select_related('user1__profile', 'user2__profile')
        matches = [m.user1 if m.user2 == user else m.user2 for m in matched_users]
        liker_ids = Like.objects.filter(liked=user).exclude(liker__in=matches).values_list('liker_id', flat=True)
        likers = User.objects.filter(id__in=liker_ids).select_related('profile')
        visitors = []
        from users.api.serializers import UserSerializer
        data = {
            'matches': UserSerializer(matches, many=True).data,
            'likers': UserSerializer(likers, many=True).data,
            'visitors': UserSerializer(visitors, many=True).data,
        }
        return Response(data)

class LikeProfileView(APIView):
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
        return Response({"status": "Beğeni başarılı.", "is_match": is_match}, status=status.HTTP_201_CREATED)

class PassProfileView(APIView):
    def post(self, request, user_id, *args, **kwargs):
        passer = request.user
        try:
            passed = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        if not Pass.objects.filter(passer=passer, passed=passed).exists():
            Pass.objects.create(passer=passer, passed=passed)
        return Response({"status": "Geçme işlemi başarılı."}, status=status.HTTP_201_CREATED)