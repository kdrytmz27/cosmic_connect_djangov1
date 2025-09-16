# notifications/logic.py

from .models import Notification
from .utils import send_fcm_push_notification

def create_and_send_notification(recipient, sender, notification_type, message, fcm_title, fcm_body, fcm_data=None):
    """
    Veritabanına bildirim kaydı oluşturur ve FCM üzerinden anlık bildirim gönderir.
    """
    # 1. Veritabanına kaydet
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        message=message
    )
    
    # 2. Anlık bildirim gönder
    send_fcm_push_notification(
        user_id=recipient.id,
        title=fcm_title,
        body=fcm_body,
        data=fcm_data
    )

# Farklı bildirim türleri için yardımcı fonksiyonlar
def send_new_like_notification(liker, liked_user):
    create_and_send_notification(
        recipient=liked_user,
        sender=liker,
        notification_type=Notification.NotificationType.NEW_LIKE,
        message=f"{liker.username} seni beğendi.",
        fcm_title="Yeni Bir Beğenin Var! ✨",
        fcm_body=f"{liker.username} profilini beğendi. Göz atmak ister misin?",
        fcm_data={'type': 'new_like', 'sender_username': liker.username}
    )

def send_new_match_notification(user1, user2):
    # Her iki kullanıcıya da bildirim gönder
    for recipient, sender in [(user1, user2), (user2, user1)]:
        create_and_send_notification(
            recipient=recipient,
            sender=sender,
            notification_type=Notification.NotificationType.NEW_MATCH,
            message=f"{sender.username} ile eşleştin.",
            fcm_title="Yeni Bir Eşleşme! 🎉",
            fcm_body=f"{sender.username} ile eşleştin! Şimdi sohbet etme zamanı.",
            fcm_data={'type': 'new_match', 'match_username': sender.username}
        )

def send_new_message_notification(sender, recipient, message_content):
    create_and_send_notification(
        recipient=recipient,
        sender=sender,
        notification_type=Notification.NotificationType.NEW_MESSAGE,
        message=f"{sender.username}: {message_content[:50]}...",
        fcm_title=f"Yeni Mesaj: {sender.username}",
        fcm_body=message_content,
        fcm_data={'type': 'new_message', 'sender_username': sender.username}
    )