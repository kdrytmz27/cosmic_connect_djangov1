# Lütfen bu kodu kopyalayıp interactions/tasks.py dosyasının içine yapıştırın.

import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.db.models.signals import post_save
from users.models import Profile, trigger_astrology_processing
from .models import Compatibility, DailyMatch, Block
from .logic import calculate_synastry_score 
from astrology.client import cosmic_api_client

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def calculate_compatibilities_for_user(user_id: int):
    try:
        main_user = User.objects.select_related('profile').get(id=user_id)
        if not all([main_user.profile.birth_date, main_user.profile.birth_time, main_user.profile.latitude, main_user.profile.longitude]):
            return f"Uyumluluk hesaplama atlandı: {main_user.username} profili hazır değil."
    except User.DoesNotExist:
        return f"Hata: {user_id} ID'li kullanıcı bulunamadı."
    
    other_users = User.objects.select_related('profile').filter(
        is_active=True,
        profile__is_birth_chart_calculated=True
    ).exclude(id=user_id)

    compatibilities_to_update_or_create = []

    p1 = main_user.profile
    p1_data = {
        "lat": p1.latitude, "lon": p1.longitude,
        "date": p1.birth_date.strftime('%Y-%m-%d'),
        "time": p1.birth_time.strftime('%H:%M')
    }

    for other_user in other_users:
        p2 = other_user.profile
        p2_data = {
            "lat": p2.latitude, "lon": p2.longitude,
            "date": p2.birth_date.strftime('%Y-%m-%d'),
            "time": p2.birth_time.strftime('%H:%M')
        }
        
        try:
            aspects = cosmic_api_client.get_synastry_aspects(p1_data, p2_data)
            if not aspects:
                continue

            score, breakdown = calculate_synastry_score(aspects)
            
            user1, user2 = sorted([main_user, other_user], key=lambda u: u.id)
            
            compatibilities_to_update_or_create.append(
                Compatibility(
                    user1=user1, 
                    user2=user2, 
                    score=score, 
                    breakdown=breakdown
                )
            )
        except Exception as e:
            logger.error(f"{p1.user.username} ve {p2.user.username} için sinastri hesaplanırken hata: {e}")
            continue

    if compatibilities_to_update_or_create:
        with transaction.atomic():
            Compatibility.objects.filter(Q(user1=main_user) | Q(user2=main_user)).delete()
            Compatibility.objects.bulk_create(compatibilities_to_update_or_create)
            
        logger.info(f"'{main_user.username}' için {len(compatibilities_to_update_or_create)} kullanıcı ile sinastri uyumluluk skorları kaydedildi.")
        
        main_user.profile.is_birth_chart_calculated = True
        post_save.disconnect(trigger_astrology_processing, sender=Profile)
        main_user.profile.save(update_fields=['is_birth_chart_calculated'])
        post_save.connect(trigger_astrology_processing, sender=Profile)
        logger.info(f"'{main_user.username}' için is_birth_chart_calculated durumu True olarak işaretlendi (sinyal tetiklenmedi).")

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