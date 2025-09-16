# subscriptions/logic.py

from datetime import timedelta
from django.utils import timezone
from .models import UserSubscription

def grant_premium_access(user, plan):
    """
    Bir kullanıcıya belirli bir abonelik paketinin süresi kadar premium erişim hakkı tanır.
    Mevcut bir aboneliği varsa, süresini uzatır.
    """
    now = timezone.now()
    
    # Kullanıcının mevcut aktif aboneliğini bul
    subscription, created = UserSubscription.objects.get_or_create(
        user=user,
        defaults={'plan': plan, 'start_date': now, 'end_date': now + timedelta(days=plan.duration_days)}
    )

    if not created:
        # Eğer zaten bir aboneliği varsa
        # Bitiş tarihi geçmişse, bugünden başlat.
        # Geçmemişse, mevcut bitiş tarihinin üzerine ekle.
        start_date = subscription.end_date if subscription.end_date > now else now
        subscription.end_date = start_date + timedelta(days=plan.duration_days)
        subscription.plan = plan
        subscription.is_active = True
        subscription.save()
    
    # Kullanıcının profilindeki `is_premium` alanını güncelle
    user.profile.is_premium = True
    user.profile.save(update_fields=['is_premium'])
    
    return subscription