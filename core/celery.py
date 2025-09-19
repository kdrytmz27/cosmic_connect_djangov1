import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

# GÜNCELLENDİ: Windows uyumluluğu için gevent havuzunu kullan
app.conf.update(
    task_always_eager=False,
    task_eager_propagates=False,
    worker_pool = 'gevent' # Bu satırı ekledik
)

app.autodiscover_tasks()