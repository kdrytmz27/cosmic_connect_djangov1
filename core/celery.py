# core/celery.py

import os
from celery import Celery

# Django'nun settings modülünü Celery'nin bulmasını sağla.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# 'CELERY' namespace'ini kullanarak Django ayarlarından Celery'i yapılandır.
# Yani settings.py dosyasındaki tüm CELERY_ ile başlayan ayarları okuyacak.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app'lerindeki tüm task modüllerini (tasks.py) otomatik olarak bul.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')