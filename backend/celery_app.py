import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpola.settings')
app = Celery('mpola')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
