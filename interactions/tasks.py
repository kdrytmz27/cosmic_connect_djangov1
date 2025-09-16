# interactions/tasks.py

import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import Compatibility, DailyMatch, Block
from .logic import calculate_compatibility_score

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def calculate_compatibilities_for_user(user_id: int):
    try:
        main_user = User.objects.select_related('profile').get(id=user_id)
        if not main_user.profile.sun_sign:
            return f"Uyumluluk hesaplama atlandı: {main_user.username} profili hazır değil."
    except User.DoesNotExist:
        return f"Hata: {user_id} ID'li kullanıcı bulunamadı."
    
    other_users = User.objects.select_related('profile').filter(
        is_active=True, profile__sun_sign__isnull=False
    ).exclude(id=user_id)

    compatibilities_to_create = []
    for other_user in other_users:
        score = calculate_compatibility_score(main_user.profile, other_user.profile)
        user1, user2 = sorted([main_user, other_user], key=lambda u: u.id)
        compatibilities_to_create.append(
            Compatibility(user1=user1, user2=user2, score=score)
        )

    if compatibilities_to_create:
        with transaction.atomic():
            # Eski skorları sil (sadece bu kullanıcıyı içerenleri)
            Compatibility.objects.filter(Q(user1=main_user) | Q(user2=main_user)).delete()
            # Yeni skorları toplu olarak ekle
            Compatibility.objects.bulk_create(compatibilities_to_create, ignore_conflicts=True)
        logger.info(f"'{main_user.username}' için {len(other_users)} kullanıcı ile uyumluluk skorları kaydedildi.")

@shared_task
def generate_daily_matches_task():
    today = timezone.now().date()
    active_users = User.objects.filter(is_active=True, profile__sun_sign__isnull=False)

    for user in active_users:
        if DailyMatch.objects.filter(user=user, date=today).exists():
            continue

        blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
        
        best_match = Compatibility.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).exclude(
            Q(user1_id__in=blocked_ids) | Q(user2_id__in=blocked_ids)
        ).order_by('-score').first()

        if best_match:
            matched_user = best_match.user1 if best_match.user2 == user else best_match.user2
            DailyMatch.objects.create(user=user, matched_user=matched_user, date=today)
            logger.info(f"{user.username} için günün eşleşmesi: {matched_user.username}")