# Lütfen bu kodu kopyalayıp astrology/tasks.py dosyasının içine yapıştırın.

import base64
import logging
from celery import shared_task
from django.apps import apps
from django.db.models.signals import post_save # YENİ IMPORT
from users.models import Profile, trigger_astrology_processing # YENİ IMPORT
from .client import cosmic_api_client

from interactions.tasks import calculate_compatibilities_for_user

logger = logging.getLogger(__name__)

SIGN_TRANSLATION_MAP = {
    'Koç': 'Aries', 'Boğa': 'Taurus', 'İkizler': 'Gemini', 'Yengeç': 'Cancer',
    'Aslan': 'Leo', 'Başak': 'Virgo', 'Terazi': 'Libra', 'Akrep': 'Scorpio',
    'Yay': 'Sagittarius', 'Oğlak': 'Capricorn', 'Kova': 'Aquarius', 'Balık': 'Pisces',
    'Aries': 'Aries', 'Taurus': 'Taurus', 'Gemini': 'Gemini', 'Cancer': 'Cancer',
    'Leo': 'Leo', 'Virgo': 'Virgo', 'Libra': 'Libra', 'Scorpio': 'Scorpio',
    'Sagittarius': 'Sagittarius', 'Capricorn': 'Capricorn', 'Aquarius': 'Aquarius', 'Pisces': 'Pisces'
}

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_astrological_data_for_profile(self, profile_id: int):
    Profile = apps.get_model('users', 'Profile')
    try:
        profile = Profile.objects.get(pk=profile_id)
    except Profile.DoesNotExist:
        logger.warning(f"Astroloji görevi: Profile ID {profile_id} bulunamadı.")
        return

    if not all([profile.birth_date, profile.birth_time, profile.latitude, profile.longitude]):
        logger.error(f"Profile ID {profile.id} için astrolojik hesaplama atlandı (eksik lat/lon/tarih/saat).")
        return

    date_str = profile.birth_date.strftime('%Y-%m-%d')
    time_str = profile.birth_time.strftime('%H:%M')
    lat_float = profile.latitude
    lon_float = profile.longitude

    try:
        # 1. Aşama: Astrolojik Verileri Çek
        chart_data = cosmic_api_client.get_full_chart_data(
            lat=lat_float, lon=lon_float, date=date_str, time=time_str
        )
        if not chart_data:
            raise ValueError("API'den /full-chart için boş veri alındı.")

        planets_data = chart_data.get('planets', [])
        planets_map = {p['planet'].lower(): SIGN_TRANSLATION_MAP.get(p.get('sign')) for p in planets_data}
        ascendant_data = chart_data.get('main_points', {}).get('ascendant', {})
        
        profile.sun_sign = planets_map.get('sun')
        profile.moon_sign = planets_map.get('moon')
        profile.rising_sign = SIGN_TRANSLATION_MAP.get(ascendant_data.get('sign'))
        profile.mercury_sign = planets_map.get('mercury')
        profile.venus_sign = planets_map.get('venus')
        profile.mars_sign = planets_map.get('mars')
        
        balance_data = chart_data.get("balance", {})
        profile.insights_data = {"elements": balance_data.get("elements"), "modes": balance_data.get("modalities")}

        # 2. Aşama: Harita Görselini Çek
        image_bytes = cosmic_api_client.get_wheel_chart_image(
            lat=lat_float, lon=lon_float, date=date_str, time=time_str
        )
        if image_bytes:
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            profile.natal_chart_png_base64 = f"data:image/png;base64,{encoded_image}"
        
        # --- GÜVENLİK DEĞİŞİKLİĞİ: SİNYALİ GEÇİCİ OLARAK DEVRE DIŞI BIRAK ---
        # Bu, aşağıdaki profile.save() komutunun döngüye yol açmasını engeller.
        post_save.disconnect(trigger_astrology_processing, sender=Profile)
        
        profile.save()
        
        # Sinyali hemen tekrar bağla ki normal kullanıcı işlemleri için çalışmaya devam etsin.
        post_save.connect(trigger_astrology_processing, sender=Profile)

        logger.info(f"Profile ID {profile.id} için astrolojik veriler ve harita başarıyla kaydedildi (sinyal tetiklenmedi).")

        # 4. Aşama: Uyumluluk hesaplama görevini tetikle
        calculate_compatibilities_for_user.delay(user_id=profile.user.id)
        logger.info(f"Uyumluluk hesaplama görevi, '{profile.user.username}' için tetiklendi.")

    except Exception as e:
        # Olası bir hata durumunda sinyalin tekrar bağlandığından emin ol.
        post_save.connect(trigger_astrology_processing, sender=Profile)
        logger.error(f"Profile ID {profile_id} işlenirken bir hata oluştu: {e}", exc_info=True)
        raise self.retry(exc=e)