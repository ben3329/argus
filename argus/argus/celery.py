import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
app = Celery('argus', broker='redis://redis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()