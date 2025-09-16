# core/__init__.py

# Bu, Django başladığında Celery app'imizin her zaman yüklenmesini sağlar.
from .celery import app as celery_app

__all__ = ('celery_app',)