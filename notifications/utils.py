# notifications/utils.py

import logging
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, messaging
from users.models import Device

logger = logging.getLogger(__name__)

# Firebase Admin SDK'yı sadece bir kez başlat
try:
    if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH.exists():
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            firebase_admin.initialize_app(cred)
except Exception as e:
    logger.error(f"Firebase Admin SDK başlatılamadı: {e}")

def send_fcm_push_notification(user_id, title, body, data=None):
    """
    Belirli bir kullanıcıya ait tüm aktif cihazlara FCM bildirimi gönderir.
    """
    if not firebase_admin._apps:
        logger.warning("Firebase Admin SDK başlatılmadığı için bildirim gönderilemedi.")
        return

    devices = Device.objects.filter(user_id=user_id, is_active=True)
    registration_tokens = [device.fcm_token for device in devices]

    if not registration_tokens:
        logger.info(f"Kullanıcı {user_id} için aktif cihaz bulunamadı, bildirim gönderilmedi.")
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=registration_tokens,
        data=data or {},
        android=messaging.AndroidConfig(
            priority='high',
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True,
                )
            )
        )
    )

    try:
        response = messaging.send_multicast(message)
        logger.info(f'{response.success_count} bildirim başarıyla gönderildi, {response.failure_count} başarısız oldu.')
        # Başarısız token'ları veritabanından temizleme mantığı eklenebilir.
    except Exception as e:
        logger.error(f"FCM bildirimi gönderilirken hata oluştu: {e}")